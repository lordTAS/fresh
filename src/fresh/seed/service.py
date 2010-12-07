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
from datetime          import datetime, timedelta
from Exscriptd.xml     import get_hosts_from_etree
from fresh.seed.Config import Config
from functools         import partial

config = Config(__service__.config_file('config.xml'))
seeddb = config.get_seeddb()

def run(order):
    __service__.set_order_status(order, 'running')
    sec   = timedelta(seconds = 1)
    start = datetime.utcnow().replace(microsecond = 0) - sec

    # Variables in an order are always lists; expand those into
    # strings.
    hosts = get_hosts_from_etree(order.xml)
    for host in hosts:
        for key, value in host.get_all().iteritems():
            host.set(key, value[0])

    # Import the hosts, while preserving the values in other columns.
    fields = ('address', 'name', 'path', 'country', 'city')
    seeddb.save_host(hosts, fields)

    # Get rid of all hosts that are no longer known.
    seeddb.delete_old_hosts(start)

def check(order):
    order.set_description('Update the host database')
    hosts = get_hosts_from_etree(order.xml)
    if not hosts:
        return False
    for host in hosts:
        if len(host.get('path')) == 0:
            return False
        if len(host.get('country')) == 0:
            return False
        if len(host.get('city')) == 0:
            return False
    return True

def enter(order):
    callback = partial(run, order)
    __service__.enqueue(order, callback, 'update')
    __service__.set_order_status(order, 'queued')
