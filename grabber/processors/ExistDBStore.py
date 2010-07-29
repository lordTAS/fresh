from pyexist import ExistDB

class ExistDBStore(object):
    def __init__(self, host, port, user, password, collection):
        uri     = user + ':' + password + '@' + host + ':' + port
        self.db = ExistDB(uri, collection)

    def start(self, provider, conn, **kwargs):
        host     = conn.get_host()
        hostname = host.get('__real_hostname__')
        filename = kwargs.get('filename')
        document = kwargs.get('document').replace('{hostname}', hostname)
        content  = provider.store.get(conn, filename)
        self.db.store(document, content)
