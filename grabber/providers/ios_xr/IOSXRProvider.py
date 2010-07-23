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
        conn.execute('terminal len 0')
        conn.execute('terminal width 0')
        conn.execute('terminal exec prompt no-timestamp')
        conn.set_timeout(1 * 60)

        # Define a more reliable prompt.
        hostname = self.get_hostname(conn)
        prompt   = r'[\r\n]\S+' + hostname + r'[#>] ?$'
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
