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
import tarfile
from tempfile      import mkdtemp
from shutil        import move, rmtree
from Exscriptd.xml import get_hosts_from_etree

class Packager(object):
    def __init__(self,
                 in_dir,
                 out_dir,
                 out_name,
                 send_to,
                 db,
                 profiles,
                 format    = 'bz2',
                 overwrite = False):
        self.in_dir    = in_dir
        self.out_dir   = out_dir
        self.out_name  = out_name
        self.send_to   = send_to
        self.format    = format
        self.overwrite = overwrite
        self.seeddb    = db
        self.profiles  = profiles

        if format not in ('directory', 'tar', 'gzip', 'bz2'):
            raise Exception('unknown format: %s' % self.format)

    def describe(self):
        outpath = os.path.join(self.out_dir, self.out_name)
        if self.format == 'directory':
            descr = 'Export a directory to %s' % outpath
        else:
            descr = 'Create a %s package at %s' % (self.format, outpath)
        for handler in self.send_to:
            descr += '. ' + handler.describe()
        return descr

    def get_seedhost_from_name(self, name):
        host = self.seeddb.get_host(name = name)
        if not host:
            raise Exception('unknown host: %s' % name)
        return host

    def _mktar(self, dirname):
        filename = os.path.join(self.out_dir, self.out_name)
        if self.overwrite and os.path.exists(filename):
            os.remove(filename)
        if self.format == 'tar':
            tar = tarfile.open(filename, 'w', dereference = True)
        elif self.format == 'gzip':
            tar = tarfile.open(filename, 'w:gz', dereference = True)
        elif self.format == 'bz2':
            tar = tarfile.open(filename, 'w:bz2', dereference = True)
        else:
            raise Exception('unknown tar format: %s' % self.format)

        for dir in os.listdir(dirname):
            subdir = os.path.join(dirname, dir)
            tar.add(subdir, dir)
        tar.close()

    def run(self, order):
        tmp_dir = mkdtemp()

        for host in get_hosts_from_etree(order.xml):
            seedhost = self.get_seedhost_from_name(host.get_name())
            address  = seedhost.get_address()
            hostname = seedhost.get_name()
            src_path = seedhost.get('path')
            dst_path = host.get('path')[0]
            dst_dir  = os.path.join(tmp_dir, dst_path)
            vars     = {'hostname': hostname,
                        'address':  address,
                        'os':       seedhost.get('os')}

            for profile in self.profiles:
                if not profile.test_condition(vars):
                    continue
                for name, from_name in profile.files:
                    src = os.path.join(self.in_dir, src_path, from_name)
                    dst = os.path.join(dst_dir, name)
                    dst = dst.replace('{address}',  address)
                    dst = dst.replace('{hostname}', hostname)
                    if os.path.exists(src):
                        if not os.path.exists(dst_dir):
                            os.makedirs(dst_dir)
                        os.symlink(src, dst)

        path = os.path.join(self.out_dir, self.out_name)
        if self.format == 'directory':
            if not os.path.exists(path):
                os.makedirs(path)
            if self.overwrite:
                for file in os.listdir(path):
                    file = os.path.join(path, file)
                    rmtree(file)
            for file in os.listdir(tmp_dir):
                file = os.path.join(tmp_dir, file)
                move(file, path)
        else:
            self._mktar(tmp_dir)
        rmtree(tmp_dir)

        for handler in self.send_to:
            handler.send(path)
