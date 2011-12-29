# Copyright (C) 2007-2011 Samuel Abels.
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
from Processor import Processor
from Exscriptd.util import find_module_recursive

class InvokeModule(Processor):
    def __init__(self, module):
        self.module = find_module_recursive(module_name)

    def start(self, provider, host, conn, **kwargs):
        return self.module.__dict__['start'](provider, host, conn)

    def delete(self, provider, host, **kwargs):
        try:
            self.module.__dict__['delete'](provider, host)
        except Exception, e:
            logger.error('%s: error during delete: %s' % (label, str(e)))
        else:
            logger.info('%s: deleted %s' % (label, document))
