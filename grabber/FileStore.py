import os

class FileStore(object):
    def __init__(self, base_dir):
        self.base_dir = base_dir
        if not os.path.isdir(self.base_dir):
            os.makedirs(self.base_dir)

    def get_path(self, conn, filename = None):
        host     = conn.get_host()
        hostname = host.get('__real_hostname__')
        path     = host.get('__path__')
        host_dir = os.path.join(self.base_dir, path)
        if filename:
            return os.path.join(host_dir, filename)
        return host_dir

    def store(self, conn, filename, content):
        host_dir = self.get_path(conn)
        filename = self.get_path(conn, filename)

        if not os.path.isdir(host_dir):
            os.makedirs(host_dir)

        # Save to disk.
        if os.path.isfile(filename):
            os.remove(filename)
        file = open(filename, 'w')
        file.write(content)
        file.close()
        return filename

    def get(self, conn, filename):
        return open(self.get_path(conn, filename)).read()
