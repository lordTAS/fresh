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
import time
from Exscript.util import template

class Provisioner(object):
    def __init__(self, seeddb):
        self.seeddb = seeddb

    def get_seedhost_from_name(self, name):
        host = self.seeddb.get_host(name = name)
        if not host:
            raise Exception('unknown host: %s' % name)
        return host

    def run(self, script, job, host, conn):
        conn.authenticate()
        template.eval(conn, script, **host.get_all())
        conn.close(True)
