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
from lxml import etree
from Processor import Processor

class LineSplitProcessor(Processor):
    def __init__(self):
        pass

    def start(self, provider, host, conn, **kwargs):
        outfile = kwargs.get('filename')

        # Create the XML document.
        xml = etree.Element('xml', hostname = host.get_name())
        for n, line in enumerate(conn.response.split('\n')):
            etree.SubElement(xml, 'line', number = str(n + 1)).text = line
        xml = etree.tostring(xml)

        # Write to file system.
        provider.store.store(provider, host, outfile, xml)
