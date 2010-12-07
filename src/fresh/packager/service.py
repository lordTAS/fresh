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
from Exscriptd.xml         import get_hosts_from_etree
from fresh.packager.Config import Config
from functools             import partial

config = Config(__service__.config_file('config.xml'))

def run(order):
    packager = config.get_packager()
    order.set_description(packager.describe())
    __service__.set_order_status(order, 'running')
    packager.run(order)

def check(order):
    order.set_description('Export to a directory or package')
    hosts = get_hosts_from_etree(order.xml)
    if not hosts:
        return False
    for host in hosts:
        if len(host.get('path')) == 0:
            return False
    return True

def enter(order):
    callback = partial(run, order)
    __service__.enqueue(order, callback, 'update')
    __service__.set_order_status(order, 'queued')
