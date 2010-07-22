from pyexist import ExistDB

class ExistDBStore(object):
    def __init__(self, **kwargs):
        host       = kwargs.get('host')
        port       = kwargs.get('port')
        user       = kwargs.get('user')
        password   = kwargs.get('password')
        collection = kwargs.get('collection')
        uri        = user + ':' + password + '@' + host + ':' + port
        self.db    = ExistDB(uri, collection)
