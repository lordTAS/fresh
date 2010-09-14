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
"""
The API for updating the list of collected hosts.
"""

import os
from sqlalchemy        import create_engine
from Exscriptd         import ConfigReader
from fresh.seed.HostDB import HostDB

class Config(ConfigReader):
    def __init__(self, filename):
        ConfigReader.__init__(self, filename)
        element     = self.cfgtree.find('seed')
        db_name     = element.find('database').text
        self.hostdb = self.init_database_from_name(db_name)

    def init_database_from_name(self, name):
        element = self.cfgtree.find('database[@name="%s"]' % name)
        dbn     = element.find('dbn').text
        print 'Creating database connection for', dbn
        engine  = create_engine(dbn)
        db      = HostDB(engine)
        print 'Initializing database tables...'
        db.install()
        return db

    def get_hostdb(self):
        return self.hostdb
