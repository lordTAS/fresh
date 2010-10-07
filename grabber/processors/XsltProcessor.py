# Copyright (C) 2007-2010 Samuel Abels.
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
import os, time
from StringIO import StringIO
from lxml     import etree

class XsltProcessor(object):
    def __init__(self,
                 xsl_dir,
                 add_hostname  = False,
                 add_address   = False,
                 add_timestamp = False):
        self.xsl_dir       = xsl_dir
        self.add_hostname  = add_hostname
        self.add_address   = add_address
        self.add_timestamp = add_timestamp

    def start(self, provider, conn, **kwargs):
        xslt_file = kwargs.get('xslt')
        xsd_file  = kwargs.get('xsd')
        infile    = kwargs.get('input')
        outfile   = kwargs.get('output')
        if not xslt_file.startswith('/'):
            xslt_file = os.path.join(self.xsl_dir, xslt_file)
        if xsd_file and not xsd_file.startswith('/'):
            xsd_file = os.path.join(self.xsl_dir, xsd_file)

        # Transform.
        xsl       = etree.parse(xslt_file)
        transform = etree.XSLT(xsl)
        path      = provider.store.get_path(conn, infile)
        input     = provider.store.get(conn, infile)
        doc       = etree.parse(StringIO(input), base_url = path)
        result    = transform(doc)

        # Add the address and a timestamp field to the root node in the resulting
        # XML.
        if self.add_address:
            address = conn.get_host().get_address()
            result.getroot().set('address', address)
        if self.add_hostname:
            hostname = conn.get_host().get_name()
            result.getroot().set('name', hostname)
        if self.add_timestamp:
            ts = time.asctime()
            etree.SubElement(result.getroot(), 'last-update').text = ts

        # Validate.
        if xsd_file:
            xsd    = etree.parse(xsd_file)
            schema = etree.XMLSchema(xsd)
            schema.assertValid(result)

        # Write.
        provider.store.store(conn, outfile, str(result))
