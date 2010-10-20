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
from Exscript.util.mail      import Mail
from Exscriptd               import ConfigReader
from fresh.seed.HostDB       import HostDB
from fresh.packager.Profile  import Profile
from fresh.packager.Packager import Packager
from fresh.packager.Mailer   import Mailer

class Config(ConfigReader):
    def __init__(self, filename):
        ConfigReader.__init__(self, filename)
        element       = self.cfgtree.find('seed')
        self.profiles = {}

    def _init_seeddb_from_name(self, name):
        element = self.cfgtree.find('database[@name="%s"]' % name)
        dbn     = element.find('dbn').text
        #print 'Creating database connection for', dbn
        engine  = create_engine(dbn)
        db      = HostDB(engine)
        #print 'Initializing database tables...'
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

    def init_mailer_from_name(self, name):
        element = self.cfgtree.find('mailer[@name="%s"]' % name)
        if element is None:
            raise Exception('no such mailer: %s' % name)

        mail = Mail()
        mail.set_sender(element.find('from').text)
        mail.set_to(element.find('to').text)
        mail.set_subject(element.find('subject').text)
        mail.set_body(element.find('body').text)

        server = element.find('server').text
        return Mailer(server, mail)

    def get_packager(self):
        element   = self.cfgtree.find('packager')
        in_dir    = element.find('input-dir').text
        out_dir   = element.find('package-dir').text
        out_name  = element.find('package-name').text
        format    = element.find('format').text
        overwrite = element.find('overwrite') is not None
        dbname    = element.find('database').text
        db        = self._init_seeddb_from_name(dbname)
        profiles  = []
        for profile_elem in element.iterfind('profile'):
            profile_name = profile_elem.text
            profile      = self.init_profile_from_name(profile_name)
            profile_cond = profile_elem.get('if')
            if profile_cond is not None:
                profile.set_condition(profile_cond)
            profiles.append(profile)

        send_to = []
        for item in element.iterfind('send-to'):
            mailer = self.init_mailer_from_name(item.text)
            send_to.append(mailer)

        return Packager(in_dir,
                        out_dir,
                        out_name,
                        send_to,
                        db,
                        profiles,
                        format    = format,
                        overwrite = overwrite)
