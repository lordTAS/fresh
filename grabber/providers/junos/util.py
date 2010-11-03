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
from lxml     import etree
from StringIO import StringIO

def remove_passwords_from_config(config):
    patterns = (re.compile(r'(.*authentication-key) (".+")'),
                re.compile(r'(.*encrypted-password) (".+")'))

    lines = []
    for line in config.split('\n'):
        for regex in patterns:
            line = regex.sub(r'\1 "REMOVED"', line)
        lines.append(line)
    return '\n'.join(lines)

def remove_descriptions_from_config(config):
    regex = re.compile(r'(.*description) (.+)')
    lines = []
    for line in config.split('\n'):
        line = regex.sub(r'\1 REMOVED', line)
        lines.append(line)
    return '\n'.join(lines)

def remove_passwords_from_xml(xml):
    tree = etree.parse(StringIO(xml))
    for elem in tree.iter():
        if elem.tag in ('key',
                        'password',
                        'authentication-key',
                        'encrypted-password'):
            elem.text = 'REMOVED'
    return etree.tostring(tree)

def remove_descriptions_from_xml(xml):
    tree = etree.parse(StringIO(xml))
    for elem in tree.iter():
        if elem.tag == 'description':
            elem.text = 'REMOVED'
    return etree.tostring(tree)
