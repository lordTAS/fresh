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
import re
from providers            import Provider
from Exscript.util.match  import first_match
from providers.junos.util import remove_passwords_from_config,    \
                                 remove_passwords_from_xml,       \
                                 remove_descriptions_from_config, \
                                 remove_descriptions_from_xml

class JunOSProvider(Provider):
    def get_hostname(self, conn):
        host = conn.get_host()
        if host.get('__cfg_hostname__'):
            return host.get('__cfg_hostname__')
        conn.execute('show version | match ^Hostname')
        hostname = first_match(conn, r'Hostname: (\S+)')
        host.set('__cfg_hostname__', hostname)
        return hostname

    def _cleanup_xml(self, xml):
        ns_url  = 'http://xml.juniper.net/junos/'
        ns_type = '(?:chassis|interface)'
        ns      = '("' + ns_url + ')\S+(/junos-' + ns_type + '")'
        ns_re   = re.compile(ns)
        return ns_re.sub(r'\1VERSION\2', xml)

    def remove_passwords_from_config(self, config):
        return remove_passwords_from_config(config)

    def remove_descriptions_from_config(self, config):
        return remove_descriptions_from_config(config)

    def remove_passwords_from_xml(self, xml):
        return remove_passwords_from_xml(xml)

    def remove_descriptions_from_xml(self, xml):
        return remove_descriptions_from_xml(xml)

    def init(self, conn):
        conn.autoinit()
        conn.set_timeout(20 * 60)

        # Define a more reliable prompt.
        hostname = self.get_hostname(conn)
        prompt   = r'[\r\n]\w+@' + re.escape(hostname) + r'[#>] ?$'
        conn.set_prompt(re.compile(prompt))

        # Whenever connection.execute() is called, clean
        # the response up.
        oldexecute = conn.execute
        def execute_wrapper(command):
            oldexecute(command)
            response = conn.response.translate(None, '\r\x00')

            # Strip the command from the response.
            response = response.split('\n')
            response.pop(0)
            conn.response = '\n'.join(response) + '\n'

            # HACK: Cleanup XML namespaces to make them more suitable for
            # conversion using XSLT.
            if '| display xml' in command:
                conn.response = self._cleanup_xml(conn.response)

        conn.execute = execute_wrapper
