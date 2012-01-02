# Copyright (C) 2007-2011 Samuel Abels.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
import os
import time
from util import apply_xslt
from StringIO import StringIO
from lxml import etree
from Processor import Processor

def _find_or_create(node, path, value):
    for name in path.split('/'):
        if name.startswith('@'):
            node.set(name[1:], value)
            return node
        node = node.find(name)
        if node is None:
            node = etree.SubElement(node, name)
    node.text = value
    return node

class XsltProcessor(Processor):
    def __init__(self, base_dir, xml):
        xsl_dir      = xml.find('xsl-dir').text
        self.xsl_dir = os.path.join(base_dir, xsl_dir)
        self.add     = dict()
        for node in xml.iterfind('add'):
            path = node.findtext('path')
            expr = node.findtext('expression')
            self.add[path] = compile(expr, 'config', 'eval')

    def start(self, provider, host, conn, **kwargs):
        xslt_file = kwargs.get('xslt')
        xsd_file  = kwargs.get('xsd')
        infile    = kwargs.get('input')
        outfile   = kwargs.get('output')
        if not xslt_file.startswith('/'):
            xslt_file = os.path.join(self.xsl_dir, xslt_file)
        if xsd_file and not xsd_file.startswith('/'):
            xsd_file = os.path.join(self.xsl_dir, xsd_file)

        # Fetch the latest version of the file.
        path = provider.store.get_path(host, infile)
        if path is None:
            return # file not found
        input = provider.store.get(host, infile)

        # Transform.
        doc    = etree.parse(StringIO(input), base_url = path)
        xsl    = etree.parse(xslt_file)
        result = apply_xslt(xsl, doc)

        # Insert extra data into the resulting XML.
        for path, expression in self.add.iteritems():
            text = eval(expression, {'host': host, 'time': time})
            node = _find_or_create(result.getroot(), path, text)

        # Validate.
        if xsd_file:
            xsd    = etree.parse(xsd_file)
            schema = etree.XMLSchema(xsd)
            schema.assertValid(result)

        # Write.
        provider.store.store(provider, host, outfile, str(result))
