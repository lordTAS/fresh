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
import os

class FileStore(object):
    def __init__(self, base_dir):
        self.base_dir = base_dir
        if not os.path.isdir(self.base_dir):
            os.makedirs(self.base_dir)

    def get_path(self, conn, filename = None):
        host     = conn.get_host()
        path     = host.get('__path__')
        host_dir = os.path.join(self.base_dir, path)
        if filename:
            return os.path.join(host_dir, filename)
        return host_dir

    def store(self, provider, conn, filename, content, cleanpass = False):
        host_dir = self.get_path(conn)
        filename = self.get_path(conn, filename)

        if not os.path.isdir(host_dir):
            os.makedirs(host_dir)

        # Save to disk.
        if os.path.isfile(filename):
            os.remove(filename)
        file = open(filename, 'w')
        if cleanpass:
            file.write(provider.remove_passwords_from_config(content))
        else:
            file.write(content)
        file.close()
        return filename

    def get(self, conn, filename):
        return open(self.get_path(conn, filename)).read()
