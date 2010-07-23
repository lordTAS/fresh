import re
from providers           import Provider
from Exscript.util.match import first_match

class IOSProvider(Provider):
    def get_hostname(self, conn):
        host = conn.get_host()
        if host.get('__real_hostname__'):
            return host.get('__real_hostname__')
        conn.execute('show configuration | i ^hostname')
        return first_match(conn, r'hostname (\S+)')

    def init(self, conn):
        # Init the connection.
        conn.execute('term len 0')
        conn.execute('term width 0')
        conn.set_timeout(15 * 60)

        # Define a more reliable prompt.
        hostname = self.get_hostname(conn)
        prompt   = r'[\r\n]' + hostname + r'[#>] ?$'
        conn.set_prompt(re.compile(prompt))

        # Whenever connection.execute() is called, clean
        # the response up.
        oldexecute = conn.execute
        def execute_wrapper(command):
            oldexecute(command)
            response = conn.response.translate(None, '\r\x00')

            # Strip the command from the response.
            response = response.split('\n')
            if response:
                response.pop(0)
            while response and '#' + command in response[0]:
                response.pop(0)
            conn.response = '\n'.join(response) + '\n'

        conn.execute = execute_wrapper

    def start(self, conn):
        Provider.start(self, conn)
