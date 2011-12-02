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
    def __init__(self, base_dir):
        self.base_dir = base_dir
        if not os.path.isdir(self.base_dir):
            os.makedirs(self.base_dir)

    def get_path(self, host, filename = None, version = None):
        """
        Returns the full path to the host with the given name.
        If the filename is not None, the path also has the filename
        appended, where the version is either the latest version
        (if version is None), or the specified one.
        Returns None if a version does not yet exist.
        """
        path     = host.get('path')
        host_dir = os.path.join(self.base_dir, path)
        if not filename:
            return host_dir
        if version is None:
            versions = self.list_versions(host, filename)
            try:
                timestamp, version, filename = versions[0]
            except IndexError:
                return None
        return os.path.join(host_dir, filename + '.' + version)

    def get_filename_from_alias(self, host, alias):
        """
        Resolves the alias to the filename, if possible.
        """
        path     = host.get('path')
        filename = os.path.join(self.base_dir, path, alias)
        if os.path.lexists(filename):
            filename = os.path.realpath(filename)
            return os.path.basename(filename).rsplit('.', 1)[0]
        return alias

    def list_files(self, host):
        """
        Returns a list of available files for the given host.
        (Returns the basename of each file.)
        """
        path     = host.get('path')
        host_dir = os.path.join(self.base_dir, path)
        file_re  = re.compile(r'(.*)\.\w+$')
        files    = set()
        for filename in os.listdir(host_dir):
            current = os.path.join(host_dir, filename)
            if os.path.islink(current):
                continue
            match = file_re.search(filename)
            if match is None:
                continue
            files.add(match.group(1))
        return list(files)

    def list_versions(self, host, filename):
        """
        Returns a list of tuples: (timestamp, version, filename)
        Returns the most recent version first.
        (The filename is the basename of each file.)
        """
        path     = host.get('path')
        filename = os.path.join(self.base_dir, path, filename)
        file_re  = re.compile(re.escape(filename) + r'\.\w+$')
        return sorted([(os.path.getmtime(f),
                        f.split('.')[-1],
                        os.path.basename(f).rsplit('.', 1)[0])
                      for f in glob.glob(filename + '.*')
                      if file_re.match(f)], reverse = True)

    def flush_history(self, host, filename, versions):
        # Get a list of all versions (oldest first).
        path    = host.get('path')
        prefix  = os.path.join(self.base_dir, path, filename)
        file_re = re.compile(re.escape(prefix) + r'\.\w+$')
        files   = sorted([(os.path.getmtime(f), f)
                          for f in glob.glob(prefix + '.*')
                          if file_re.match(f)])

        # Delete outdated versions.
        for timestamp, filename in files[:-versions]:
            os.remove(filename)

    def alias(self, host, filename, version, name):
        if name is None:
            return
        host_dir = self.get_path(host)
        link     = os.path.join(host_dir, name)
        if os.path.lexists(link):
            os.remove(link)
        os.symlink(filename + '.' + version, link)

    def store(self,
              provider,
              host,
              filename,
              content,
              alias     = None,
              versions  = 1,
              cleanpass = False,
              cleandesc = False):
        isxml    = filename.endswith('.xml')
        host_dir = self.get_path(host)

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
        thehash = md5(content).hexdigest()
        path    = self.get_path(host, filename, thehash)
        if os.path.isfile(path):
            os.utime(path, None)
            self.alias(host, filename, thehash, alias)
            self.alias(host, filename, thehash, filename)
            self.flush_history(host, filename, versions)
            return path

        # Find the last version number.
        version_list = self.list_versions(host, filename)
        try:
            last_hash = version_list[0]
        except IndexError:
            last_hash = None

        # Save to a temporary file.
        with NamedTemporaryFile(delete = False) as tempfile:
            os.fchmod(tempfile.fileno(), 0644)
            tempfile.write(content)

        # Rename the temporary file.
        shutil.move(tempfile.name, path)
        self.alias(host, filename, thehash, alias)
        self.alias(host, filename, thehash, filename)
        self.flush_history(host, filename, versions)

        # Remember the change.
        changed = host.get('__changed__')
        changed[filename] = last_hash, thehash
        if alias:
            changed[alias] = last_hash, thehash
        return path

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
