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
from fresh.seed.SeedDB import SeedDB

def get_seeddb_from_name(config, name):
    element = config._findelem('database[@name="%s"]' % name)
    dbn     = element.find('dbn').text
    engine  = create_engine(dbn)
    db      = SeedDB(engine)
    db.install()
    return db

class Config(ConfigReader):
    def __init__(self, filename, parent):
        ConfigReader.__init__(self, filename, parent = parent)
        element     = self.cfgtree.find('seed')
        db_name     = element.find('database').text
        self.seeddb = get_seeddb_from_name(self, db_name)

    def get_seeddb(self):
        return self.seeddb
