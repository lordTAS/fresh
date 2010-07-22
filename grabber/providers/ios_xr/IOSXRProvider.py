import re
from providers           import Provider
from Exscript.util.match import first_match

class IOSXRProvider(Provider):
    def get_hostname(self, conn):
        host = conn.get_host()
        if host.get('__real_hostname__'):
            return host.get('__real_hostname__')
        conn.execute('show configuration running-config | i ^hostname')
        return first_match(conn, r'hostname (\S+)')

    def init(self, conn):
        # Init the connection.
        conn.execute('term len 0')
        conn.execute('term width 0')
        conn.set_timeout(1 * 60)

        # Define a more reliable prompt.
        hostname = self.get_hostname(conn)
        prompt   = r'[\r\n]\S+' + hostname + r'[#>] ?$'
        conn.set_prompt(re.compile(prompt))

    def start(self, conn):
        Provider.start(self, conn)
