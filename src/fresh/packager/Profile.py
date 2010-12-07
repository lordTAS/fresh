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

class Profile(object):
    def __init__(self):
        self.condition = None
        self.files     = []

    def set_condition(self, cond):
        self.condition = compile(cond, 'config', 'eval')

    def test_condition(self, vars):
        if not self.condition:
            return True
        return eval(self.condition, vars)

    def add_file(self, name, from_name):
        self.files.append((name, from_name))