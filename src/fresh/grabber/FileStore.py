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
import shutil

class FileStore(object):
    def __init__(self, base_dir):
        self.base_dir = base_dir
        if not os.path.isdir(self.base_dir):
            os.makedirs(self.base_dir)

    def get_path(self, host, filename = None):
        path     = host.get('__path__')
        host_dir = os.path.join(self.base_dir, path)
        if filename:
            return os.path.join(host_dir, filename)
        return host_dir

    def store(self,
              provider,
              host,
              filename,
              content,
              cleanpass = False,
              cleandesc = False):
        host_dir = self.get_path(host)
        filename = self.get_path(host, filename)
        isxml    = filename.endswith('.xml')

        if not os.path.isdir(host_dir):
            os.makedirs(host_dir)

        # Save to disk.
        if cleanpass and isxml:
            content = provider.remove_passwords_from_xml(content)
        elif cleanpass:
            content = provider.remove_passwords_from_config(content)
        if cleandesc and isxml:
            content = provider.remove_descriptions_from_xml(content)
        elif cleandesc:
            content = provider.remove_descriptions_from_config(content)
        if os.path.isfile(filename):
            os.remove(filename)
        with open(filename, 'w') as file:
            file.write(content)
        return filename

    def get(self, host, filename):
        with open(self.get_path(host, filename)) as file:
            return file.read()

    def delete(self, host):
        label    = host.get('__label__')
        logger   = host.get('__logger__')
        path     = host.get('path')
        host_dir = os.path.join(self.base_dir, path)
        if os.path.isdir(host_dir):
            try:
                shutil.rmtree(host_dir)
            except Exception, e:
                logger.error('%s: FileStore.delete(): %s' % (label, str(e)))
            else:
                logger.info('%s: FileStore: deleted %s' % (label, host_dir))
