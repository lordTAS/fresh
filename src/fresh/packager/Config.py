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
import base64
from sqlalchemy              import create_engine
from Exscript.util.mail      import Mail
from Exscriptd               import ConfigReader
from fresh.seed.Config       import get_seeddb_from_name
from fresh.packager.Profile  import Profile
from fresh.packager.Packager import Packager
from fresh.packager.Mailer   import Mailer
from fresh.packager.FTPPush  import FTPPush

class Config(ConfigReader):
    def __init__(self, filename, parent):
        ConfigReader.__init__(self, filename, parent = parent)
        self.profiles = {}

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
            return None

        mail = Mail()
        mail.set_sender(element.find('from').text)
        mail.set_to(element.find('to').text)
        mail.set_subject(element.find('subject').text)
        mail.set_body(element.find('body').text)

        server = element.find('server').text
        return Mailer(server, mail)

    def init_ftp_from_name(self, name):
        element = self.cfgtree.find('ftp[@name="%s"]' % name)
        if element is None:
            return None

        address  = element.find('address').text
        path     = element.find('path').text
        filename = element.find('filename').text
        user     = element.find('user').text
        password = base64.decodestring(element.find('password').text)
        return FTPPush(address, path, filename, user, password)

    def init_send_to_from_name(self, name):
        mailer = self.init_mailer_from_name(name)
        if mailer:
            return mailer
        ftp = self.init_ftp_from_name(name)
        if ftp:
            return ftp
        raise Exception('send-to: no such element: %s' % name)

    def get_packager(self):
        element   = self.cfgtree.find('packager')
        in_dir    = element.find('input-dir').text
        out_dir   = element.find('package-dir').text
        out_name  = element.find('package-name').text
        format    = element.find('format').text
        overwrite = element.find('overwrite') is not None
        dbname    = element.find('database').text
        db        = get_seeddb_from_name(self, dbname)
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
            handler = self.init_send_to_from_name(item.text)
            send_to.append(handler)

        return Packager(in_dir,
                        out_dir,
                        out_name,
                        send_to,
                        db,
                        profiles,
                        format    = format,
                        overwrite = overwrite)
