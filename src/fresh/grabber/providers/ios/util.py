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

def remove_passwords_from_config(config):
    """
    Redacts the following lines in a config::

        enable secret 5 xxxxxxxxxxxxxxxxxxxxxxxxxxx
        username NIC password 7 xxxxxxxxxxxxxxxxxxxxx
         domain-password xxxxxx
         area-password xxxxx
         set community xxxxxxxxx xxxxxxxxx
         snmp-server community xxxxxx RO 10
         snmp-server community xxxxxxxxxxxxxxxxxxx view writeNet RW 12
         snmp-server host 153.17.105.9 xxxxxxxx
         password 7 xxxxxxxxxxxxxxxxx
         tacacs-server key xxxxxxxxxxxxxxxxxxxxxxxxx
         radius-server key xxxxxxxxxxxxxxxxxxxxxxxxx
    """
    patterns = (re.compile(r'(.*username .+ password) (.+)'),
                re.compile(r'(.*password (encrypted|\d+)) (.+)'),
                re.compile(r'(.*\w+-server key) (.+)'),
                re.compile(r'(.*enable secret \d+) (.+)'),
                re.compile(r'(.*set community) (.+)'),
                re.compile(r'(.*snmp-server community) (.+)'),
                re.compile(r'(.*snmp-server host \S+) (.+)'),
                re.compile(r'(.*(area|lsp|domain)-password) (.+)'))

    lines = []
    for line in config.split('\n'):
        for regex in patterns:
            line = regex.sub(r'\1 REMOVED', line)
        lines.append(line)
    return '\n'.join(lines)

def remove_descriptions_from_config(config):
    regex = re.compile(r'(.*description) .+')
    lines = []
    for line in config.split('\n'):
        line = regex.sub(r'\1 REMOVED', line)
        lines.append(line)
    return '\n'.join(lines)
