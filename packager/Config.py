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

from sqlalchemy              import create_engine
from Exscriptd               import ConfigReader
from fresh.seed.HostDB       import HostDB
from fresh.packager.Profile  import Profile
from fresh.packager.Packager import Packager

class Config(ConfigReader):
    def __init__(self, filename):
        ConfigReader.__init__(self, filename)
        element       = self.cfgtree.find('seed')
        self.profiles = {}

    def _init_seeddb_from_name(self, name):
        element = self.cfgtree.find('database[@name="%s"]' % name)
        dbn     = element.find('dbn').text
        print 'Creating database connection for', dbn
        engine  = create_engine(dbn)
        db      = HostDB(engine)
        print 'Initializing database tables...'
        db.install()
        return db

    def init_profile_from_name(self, name):
        element = self.cfgtree.find('profile[@name="%s"]' % name)
        if element is None:
            raise Exception('no such profile: %s' % name)
        profile = Profile()
        for child in element.iterfind('link'):
            profile.add_file(child.get('name'), child.text)
        return profile

    def get_packager(self):
        element       = self.cfgtree.find('packager')
        in_dir        = element.find('input-dir').text
        out_dir       = element.find('package-dir').text
        format        = element.find('format').text
        dbname        = element.find('database').text
        db            = self._init_seeddb_from_name(dbname)
        profile_names = [e.text for e in element.iterfind('profile')]
        profiles      = [self.init_profile_from_name(n) for n in profile_names]
        return Packager(in_dir, out_dir, db, profiles, format = format)
