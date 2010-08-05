
class Grabber(object):
    def __init__(self, seeddb, processors, providers):
        self.seeddb     = seeddb
        self.processors = processors
        self.providers  = providers

    def get_path_from_address(self, address):
        host = self.seeddb.get_host(address = address)
        if not host:
            raise Exception('unknown host: %s' % address)
        return host.get('path')

    def grab(self, conn):
        # Open the connection.
        conn.open()
        conn.authenticate(wait = True)

        # Find and init the provider.
        os       = conn.guess_os()
        provider = self.providers.get(os)
        if provider is None:
            raise Exception('Error: No provider for %s found.' % repr(os))
        provider.init(conn)

        # Init default variables.
        host     = conn.get_host()
        hostname = provider.get_hostname(conn)
        address  = host.get_address()
        host.set('__path__', self.get_path_from_address(address))
        host.set('__real_hostname__', hostname or host.get_name())

        # Run.
        provider.start(conn)
