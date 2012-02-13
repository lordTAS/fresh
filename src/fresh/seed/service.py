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

config     = __service__.read_config('config.xml', Config)
queue_name = __service__.get_queue_name()
queue      = __exscriptd__.get_queue_from_name(queue_name)
seeddb     = config.get_seeddb()

def run(order, job):
    sec   = timedelta(seconds = 1)
    start = datetime.utcnow().replace(microsecond = 0) - sec

    try:
        # Import the hosts, while preserving the values in other columns.
        hosts  = get_hosts_from_etree(order.xml)
        fields = ('address',
                  'name',
                  'protocol',
                  'tcp_port',
                  'path',
                  'country',
                  'city')
        seeddb.save_host(hosts, fields)

        # Mark all hosts that are no longer known as 'deleted'.
        seeddb.mark_old_hosts(start)
    except Exception:
        logger.error(traceback.format_exc())
        raise

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
    logdir = __exscriptd__.get_order_logdir(order)
    task = __exscriptd__.create_task(order, 'Update the host database')
    task.set_logfile(logdir, 'seed.log')
    qtask = queue.enqueue(partial(run, order), 'seed')
    task.set_job_id(qtask.job_ids.pop())
