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
import os, tarfile
from tempfile import mkdtemp
from shutil   import move, rmtree

class Packager(object):
    def __init__(self, in_dir, out_dir, db, profiles, format = 'bz2'):
        self.in_dir   = in_dir
        self.out_dir  = out_dir
        self.format   = format
        self.seeddb   = db
        self.profiles = profiles

        if format not in ('directory', 'tar', 'gzip', 'bz2'):
            raise Exception('unknown format: %s' % self.format)

    def get_source_path_from_address(self, address):
        host = self.seeddb.get_host(address = address)
        if not host:
            return None
        return host.get('path')

    def _mktar(self, dirname, basename):
        if self.format == 'tar':
            filename = os.path.join(self.out_dir, basename + '.tar')
            tar      = tarfile.open(filename, 'w', dereference = True)
        elif self.format == 'gzip':
            filename = os.path.join(self.out_dir, basename + '.tar.gz')
            tar      = tarfile.open(filename, 'w:gz', dereference = True)
        elif self.format == 'bz2':
            filename = os.path.join(self.out_dir, basename + '.tar.bz2')
            tar      = tarfile.open(filename, 'w:bz2', dereference = True)
        else:
            raise Exception('unknown tar format: %s' % self.format)

        for dir in os.listdir(dirname):
            subdir = os.path.join(dirname, dir)
            tar.add(subdir, dir)
        tar.close()

    def run(self, order):
        tmp_dir = mkdtemp()

        for host in order.get_hosts():
            src_path = self.get_source_path_from_address(host.get_address())
            dst_path = host.get('path')[0]

            for name, from_name in self.profiles[0].files:  #FIXME: select profile
                src = os.path.join(self.in_dir, src_path, from_name)
                dst = os.path.join(tmp_dir,     dst_path, name)
                dst = dst.replace('{hostname}', host.get_name())
                #print "ADDING", src, dst
                if os.path.exists(src):
                    os.makedirs(os.path.join(tmp_dir, dst_path))
                    os.symlink(src, dst)

        if self.format == 'directory':
            move(tmp_dir, self.out_dir)
        else:
            self._mktar(tmp_dir, str(order.id))
            rmtree(tmp_dir)
