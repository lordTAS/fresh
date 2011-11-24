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
import re
import glob
import shutil
from hashlib import md5
from tempfile import NamedTemporaryFile

class FileStore(object):
    def __init__(self, base_dir, history_dir):
        self.base_dir = base_dir
        self.history_dir = history_dir
        if not os.path.isdir(self.base_dir):
            os.makedirs(self.base_dir)
        if not os.path.isdir(self.history_dir):
            os.makedirs(self.history_dir)

    def get_path(self, host, filename = None):
        path     = host.get('__path__')
        host_dir = os.path.join(self.base_dir, path)
        if filename:
            return os.path.join(host_dir, filename)
        return host_dir

    def get_history_path(self, host, filename = None):
        path     = host.get('__path__')
        host_dir = os.path.join(self.history_dir, path)
        if filename:
            return os.path.join(host_dir, filename)
        return host_dir

    def move_to_history(self, filename, history_filename, versions):
        if not os.path.isdir(os.path.dirname(history_filename)):
            os.makedirs(os.path.dirname(history_filename))

        # Get a list of all old versions (oldest first).
        file_re = re.compile(re.escape(path) + r'\.(\w+)')
        files   = sorted([(os.path.getmtime(f), f)
                          for f in glob.glob(history_filename + '.*')
                          if file_re.match(f)])

        # Delete outdated versions.
        for timestamp, thefilename in files[:-versions]:
            os.remove(thefilename)

        # Store the additional version.
        thehash = md5(open(filename).read()).hexdigest()
        shutil.move(filename, history_filename + '.' + thehash)

    def alias(self, host, filename, name):
        if name is None:
            return
        link = self.get_path(host, name)
        if os.path.lexists(link):
            os.remove(link)
        os.symlink(filename, link)

    def store(self,
              provider,
              host,
              filename,
              content,
              alias     = None,
              versions  = 1,
              cleanpass = False,
              cleandesc = False):
        host_dir     = self.get_path(host)
        history_file = self.get_history_path(host, filename)
        filename     = self.get_path(host, filename)
        isxml        = filename.endswith('.xml')

        if not os.path.isdir(host_dir):
            os.makedirs(host_dir)

        # Pre-process the content.
        if cleanpass and isxml:
            content = provider.remove_passwords_from_xml(content)
        elif cleanpass:
            content = provider.remove_passwords_from_config(content)
        if cleandesc and isxml:
            content = provider.remove_descriptions_from_xml(content)
        elif cleandesc:
            content = provider.remove_descriptions_from_config(content)

        # If the file is unchanged just move on.
        if os.path.isfile(filename):
            hash1 = md5(content).hexdigest()
            hash2 = md5(open(filename).read()).hexdigest()
            if hash1 == hash2:
                self.alias(host, filename, alias)
                return filename

        # Save to a temporary file.
        with NamedTemporaryFile(delete = False) as tempfile:
            os.fchmod(tempfile.fileno(), 0644)
            tempfile.write(content)

        # Move the old file away (to history or just delete).
        if os.path.isfile(filename):
            self.move_to_history(filename, history_file, versions)

        # Rename the temporary file.
        shutil.move(tempfile.name, filename)
        self.alias(host, filename, alias)
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
