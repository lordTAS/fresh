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

class ExistDBStore(object):
    def __init__(self, db):
        self.db = db

    def _replace_vars(self, conn, string):
        host        = conn.get_host()
        address     = host.get_address()
        hostname    = host.get_name()
        cfghostname = host.get('__cfg_hostname__')
        string      = string.replace('{address}',     address)
        string      = string.replace('{hostname}',    hostname)
        string      = string.replace('{cfghostname}', cfghostname)
        return string

    def start(self, provider, conn, **kwargs):
        filename = kwargs.get('filename')
        document = kwargs.get('document')
        document = self._replace_vars(conn, document)
        content  = provider.store.get(conn, filename)
        self.db.store(document, content)
