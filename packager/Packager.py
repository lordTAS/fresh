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
    def __init__(self,
                 in_dir,
                 out_dir,
                 db,
                 profiles,
                 format     = 'bz2',
                 delete_dir = False):
        self.in_dir     = in_dir
        self.out_dir    = out_dir
        self.format     = format
        self.delete_dir = delete_dir
        self.seeddb     = db
        self.profiles   = profiles

        if format not in ('directory', 'tar', 'gzip', 'bz2'):
            raise Exception('unknown format: %s' % self.format)

    def get_seedhost_from_address(self, address):
        host = self.seeddb.get_host(address = address)
        if not host:
            raise Exception('unknown host: %s' % address)
        return host

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
            seedhost = self.get_seedhost_from_address(host.get_address())
            src_path = seedhost.get('path')
            dst_path = host.get('path')[0]
            dst_dir  = os.path.join(tmp_dir, dst_path)
            vars     = {'os': seedhost.get('os')}
            hostname = host.get_name()

            for profile in self.profiles:
                if not profile.test_condition(vars):
                    continue
                for name, from_name in profile.files:
                    src = os.path.join(self.in_dir, src_path, from_name)
                    dst = os.path.join(dst_dir, name)
                    dst = dst.replace('{hostname}', hostname)
                    if os.path.exists(src):
                        if not os.path.exists(dst_dir):
                            os.makedirs(os.path.join(dst_dir))
                        os.symlink(src, dst)

        if self.format == 'directory':
            if self.delete_dir:
                for file in os.listdir(self.out_dir):
                    file = os.path.join(self.out_dir, file)
                    rmtree(file)
            for file in os.listdir(tmp_dir):
                file = os.path.join(tmp_dir, file)
                move(file, self.out_dir)
        else:
            self._mktar(tmp_dir, str(order.id))
        rmtree(tmp_dir)
