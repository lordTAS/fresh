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
from Processor import Processor

class ExistDBStore(Processor):
    def __init__(self, db):
        self.db = db

    def _replace_vars(self, host, string):
        address  = host.get_address()
        hostname = host.get_name()
        string   = string.replace('{address}',  address)
        string   = string.replace('{hostname}', hostname)
        return string

    def start(self, provider, conn, **kwargs):
        host     = conn.get_host()
        filename = kwargs.get('filename')
        document = kwargs.get('document')
        document = self._replace_vars(host, document)
        content  = provider.store.get(conn, filename)
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
