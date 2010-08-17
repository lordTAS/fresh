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
from fresh.seed.Config import Config
from functools         import partial

config = Config(__service__.config_file('config.xml'))
hostdb = config.get_hostdb()

def run(service, order):
    service.set_order_status(order, 'running')

    # Delete all hosts.
    hostdb.delete_host()

    # Import new hosts.
    hostdb.save_host(order.get_hosts())

def check(service, order):
    return True # No validation needed

def enter(service, order):
    callback = partial(run, service, order)
    service.enqueue(order, callback, 'update')
    service.set_order_status(order, 'queued')
