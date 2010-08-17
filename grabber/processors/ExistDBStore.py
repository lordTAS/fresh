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
from pyexist import ExistDB

class ExistDBStore(object):
    def __init__(self, host, port, user, password, collection):
        uri     = user + ':' + password + '@' + host + ':' + port
        self.db = ExistDB(uri, collection)

    def start(self, provider, conn, **kwargs):
        host     = conn.get_host()
        hostname = host.get('__real_hostname__')
        filename = kwargs.get('filename')
        document = kwargs.get('document').replace('{hostname}', hostname)
        content  = provider.store.get(conn, filename)
        self.db.store(document, content)
