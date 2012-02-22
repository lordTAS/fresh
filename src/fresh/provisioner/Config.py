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
import os
from fresh.seed.Config import get_seeddb_from_name
from Exscriptd   import ConfigReader
from Provisioner import Provisioner

class Config(ConfigReader):
    def __init__(self, filename, parent):
        ConfigReader.__init__(self, filename, parent = parent)
        self.provisioner = None
        self._init()

    def _init(self):
        seeddb_name  = grabber_elem.find('database').text
        seeddb       = get_seeddb_from_name(self, seeddb_name)
        self.provisioner = Provisioner(seeddb)

    def get_provisioner(self):
        return self.provisioner
