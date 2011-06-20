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
import time
from Processor import Processor
from lxml import etree

class ExistDBStore(Processor):
    def __init__(self, db):
        self.db = db

    def _replace_vars(self, host, string):
        address  = host.get_address()
        hostname = host.get_name()
        string   = string.replace('{address}',  address)
        string   = string.replace('{hostname}', hostname)
        return string

    def _txt2xml(self, hostname, content):
        ts  = time.asctime()
        xml = etree.Element('xml', hostname = hostname, timestamp = ts)
        for n, line in enumerate(content.split('\n')):
            etree.SubElement(xml, 'line', number = str(n + 1)).text = line
        return etree.tostring(xml)

    def start(self, provider, host, conn, **kwargs):
        filename = kwargs.get('filename')
        document = kwargs.get('document')
        document = self._replace_vars(host, document)
        content  = provider.store.get(host, filename)

        if filename.endswith('.txt'):
            content = self._txt2xml(host.get_name(), content)

        self.db.store(document, content)

    def delete(self, provider, host, **kwargs):
        label    = host.get('__label__')
        logger   = host.get('__logger__')
        document = kwargs.get('document')
        document = self._replace_vars(host, document)
        try:
            self.db.delete(document)
        except Exception, e:
            logger.error('%s: error during delete: %s' % (label, str(e)))
        else:
            logger.info('%s: deleted %s' % (label, document))
