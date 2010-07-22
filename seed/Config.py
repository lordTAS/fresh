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
from sqlalchemy     import create_engine
from lxml           import etree
from Exscriptd.util import resolve_variables
from HostDB         import HostDB

__dirname__ = os.path.dirname(__file__)

class Config(object):
    def __init__(self, filename):
        self.cfgtree   = etree.parse(filename)
        self.variables = {}
        self.seed      = None
        self._clean_tree()
        self._init()

    def _resolve(self, text):
        if text is None:
            return None
        return resolve_variables(self.variables, text.strip())

    def _clean_tree(self):
        # Read all variables.
        for element in self.cfgtree.find('variables'):
            varname = element.tag.strip()
            value   = resolve_variables(self.variables, element.text)
            self.variables[varname] = value

        # Resolve variables everywhere.
        for element in self.cfgtree.iter():
            element.text = self._resolve(element.text)
            for attr in element.attrib:
                value                = element.attrib[attr]
                element.attrib[attr] = self._resolve(value)

    def init_database_from_name(self, name):
        element = self.cfgtree.find('database[@name="%s"]' % name)
        dbn     = element.find('dbn').text
        print 'Creating database connection for', dbn
        engine  = create_engine(dbn)
        db      = HostDB(engine)
        print 'Initializing database tables...'
        db.install()
        return db

    def _init(self):
        element     = self.cfgtree.find('seed')
        db_name     = element.find('database').text
        self.hostdb = self.init_database_from_name(db_name)

    def get_hostdb(self):
        return self.hostdb
