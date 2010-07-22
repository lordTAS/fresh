import os
from util import str2filename

class FileStore(object):
    def __init__(self, base_dir):
        self.base_dir = base_dir
        if not os.path.isdir(self.base_dir):
            os.makedirs(self.base_dir)

    def start(self, conn, **kwargs):
        host     = conn.get_host()
        hostname = host.get('__real_hostname__')
        path     = host.get('__path__')
        command  = host.get('__last_command__')
        host_dir = os.path.join(self.base_dir, path)
        filename = kwargs.get('filename', str2filename(command))
        filename = os.path.join(host_dir, filename)

        if not os.path.isdir(host_dir):
            os.makedirs(host_dir)

        # Save to disk.
        if os.path.isfile(filename):
            os.remove(filename)
        file = open(filename, 'w')
        file.write(conn.response)
        file.close()
        return filename
