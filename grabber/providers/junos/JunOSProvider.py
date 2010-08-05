import re
from providers           import Provider
from Exscript.util.match import first_match

class JunOSProvider(Provider):
    def get_hostname(self, conn):
        host = conn.get_host()
        if host.get('__real_hostname__'):
            return host.get('__real_hostname__')
        conn.execute('show version | match ^Hostname')
        return first_match(conn, r'Hostname: (\S+)')

    def _cleanup_xml(self, xml):
        ns_url  = 'http://xml.juniper.net/junos/'
        ns_type = '(?:chassis|interface)'
        ns      = '("' + ns_url + ')\S+(/junos-' + ns_type + '")'
        ns_re   = re.compile(ns)
        return ns_re.sub(r'\1VERSION\2', xml)

    def init(self, conn):
        # Init the connection.
        conn.execute('set cli screen-length 0')
        conn.execute('set cli screen-width 0')
        conn.set_error_prompt(re.compile('^(unknown|invalid|error)', re.I))
        conn.set_timeout(20 * 60)

        # Define a more reliable prompt.
        hostname = self.get_hostname(conn)
        prompt   = r'[\r\n]\w+@' + hostname + r'[#>] ?$'
        conn.set_prompt(re.compile(prompt))

        # Whenever connection.execute() is called, clean
        # the response up.
        oldexecute = conn.execute
        def execute_wrapper(command):
            oldexecute(command)
            response = conn.response.translate(None, '\r')

            # Strip the command from the response.
            response = response.split('\n')
            response.pop(0)
            conn.response = '\n'.join(response) + '\n'

            # HACK: Cleanup XML namespaces to make them more suitable for
            # conversion using XSLT.
            if '| display xml' in command:
                conn.response = self._cleanup_xml(conn.response)

        conn.execute = execute_wrapper
