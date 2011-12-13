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

config     = __service__.read_config('config.xml', Config)
queue_name = __service__.get_queue_name()
queue      = __exscriptd__.get_queue_from_name(queue_name)

def run(order, job):
    logger   = __exscriptd__.get_logger(order, 'export.log')
    packager = config.get_packager()
    __exscriptd__.set_job_name(job.id, packager.describe())
    packager.run(logger, order)

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
    logdir = __exscriptd__.get_order_logdir(order)
    task = __exscriptd__.create_task(order, 'Export a directory or package')
    task.set_logfile(logdir, 'packager.log')
    qtask = queue.enqueue(partial(run, order), 'packager')
    task.set_job_id(qtask.job_ids.pop())
