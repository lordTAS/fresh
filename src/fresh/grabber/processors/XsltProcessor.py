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
        child = node.find(name)
        if child is None:
            node = etree.SubElement(node, name)
        else:
            node = child
    node.text = value
    return node

class XsltProcessor(Processor):
    def __init__(self, base_dir, xml):
        xsl_dir      = xml.find('xsl-dir').text
        self.xsl_dir = os.path.join(base_dir, xsl_dir)
        self.add     = []
        self.debug   = False
        for node in xml.iterfind('add'):
            path = node.findtext('path')
            expr = node.findtext('expression')
            self.add.append((path, compile(expr, 'config', 'eval')))

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
        for path, expression in self.add:
            text = eval(expression, {'host': host, 'time': time})
            _find_or_create(result.getroot(), path, text)

        # Validate.
        if xsd_file:
            xsd    = etree.parse(xsd_file)
            schema = etree.XMLSchema(xsd)
            schema.assertValid(result)

        # Write.
        if self.debug:
            print str(result)
        else:
            provider.store.store(provider, host, outfile, str(result))

if __name__ == '__main__':
    import sys
    from FileStore import FileStore
    from Exscript import Host

    basedir   = os.path.dirname(os.path.dirname(__file__))
    prov_dir  = os.path.join(basedir, 'providers')
    xsd_file  = os.path.join(basedir, 'xsl', 'model.xsd')
    xslt_file = os.path.join(prov_dir, 'ios', 'xsl', 'generic.xsl')
    xml       = etree.parse(sys.argv[1])
    proc_xml  = xml.find('processor[@type="xslt"]')
    fs_dir    = os.path.expandvars(xml.findtext('file-store/basedir'))
    proc_xml.find('xsl-dir').text = basedir
    print 'Assuming file store is in', fs_dir
    class FakeProvider(object):
        store = FileStore(fs_dir)
    prov = FakeProvider()

    p       = XsltProcessor(basedir, proc_xml)
    p.debug = True
    host    = Host('m4docirom1ea.do-a-11.de.ipmb.dtag.de')
    host.set('path',    'ipmb/pe/m4docirom1ea.do-a-11.de.ipmb.dtag.de')
    host.set('country', 'mycountry')
    host.set('city',    'mycity')
    p.start(prov,
            host,
            object,
            xslt   = xslt_file,
            xsd    = xsd_file,
            input  = 'show_version.xml',
            output = 'not-used.xml')
