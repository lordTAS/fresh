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
from providers import Provider

_prompt_re = re.compile(r'[\w\-]+@(\S+):\S+[%#] $')

class ArborPeakflowProvider(Provider):
    def get_hostname(self, host, conn):
        if host.get('__cfg_hostname__'):
            return host.get('__cfg_hostname__')

        # We attempt to find the hostname by just sending a return keypress,
        # and parsing the subsequent command line prompt.
        conn.send('\r')
        index, match = conn.expect(_prompt_re)
        hostname     = match.group(1)
        host.set('__cfg_hostname__', hostname)
        return hostname

    def init(self, host, conn):
        conn.autoinit()
        conn.set_timeout(5 * 60)
