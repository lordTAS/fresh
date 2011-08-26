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
from functools import partial
from Exscriptd.xml import get_hosts_from_etree
from Exscript.util.log import log_to_file
from fresh.grabber.Config import Config

config     = __service__.read_config('config.xml', Config)
queue_name = __service__.get_queue_name()
queue      = __exscriptd__.get_queue_from_name(queue_name)
grabber    = config.get_grabber()

def run(logger, job, host, conn):
    try:
        label = grabber.get_label_from_host(host)
    except Exception, e:
        logger.error('Label not found: %s' % str(e))
        raise

    try:
        logger.info('%s: Connected.' % label)
        grabber.grab(__exscriptd__, job.id, conn, host, logger)
    except Exception, e:
        logger.error('%s: Exception: %s' % (label, repr(str(e))))
        raise

def flush(logger, job):
    grabber.flush(__exscriptd__, logger)

def check(order):
    hosts = get_hosts_from_etree(order.xml)

    if not hosts:
        descr = ''
    elif len(hosts) == 1:
        descr = 'Update !' + hosts[0].get_name()
    else:
        descr = 'Update %d hosts' % len(hosts)

    if order.xml.find('flush') is not None:
        if descr:
            descr += ' and delete deactivated ones'
        else:
            descr = 'Delete deactivated hosts'

    if not descr:
        descr = 'Order did not contain any hosts'
        order.set_description(descr)
        return False

    order.set_description(descr)
    return True

def enter(order):
    logdir = __exscriptd__.get_order_logdir(order)
    logger = __exscriptd__.get_logger(order, 'command.log')

    for host in get_hosts_from_etree(order.xml):
        # Track the status of the update per-host.
        hostname = host.get_name()
        task     = __exscriptd__.create_task(order, 'Update !%s' % hostname)
        task.set_logfile(hostname + '.log')

        # Since the order only contains a list of hostnames without any
        # other info (such as the address or path), we need to load the
        # additional attributes from the database.
        seedhost = grabber.get_seedhost_from_name(hostname)
        if not seedhost:
            logger.info('%s: Error: Address for host not found.' % hostname)
            task.close('address-not-found')
            continue

        # Enqueue the host.
        decor = log_to_file(logdir, delete = True)
        qtask = queue.run_or_ignore(seedhost, decor(partial(run, logger)))
        if qtask is None:
            logger.info('%s: Already queued, so request ignored.' % hostname)
            task.close('duplicate')
            continue

        # Associate the queued job with the task such that Exscriptd can
        # update the status of the task.
        job_id = qtask.job_ids.pop()
        task.set_job_id(job_id)
        logger.info('%s: Queued with job id %s.' % (hostname, job_id))

    # If the order contains a <flush/> tag, delete the data of all unknown
    # hosts.
    if order.xml.find('flush') is not None:
        task = __exscriptd__.create_task(order, 'Delete obsolete hosts')
        task.set_logfile('flush.log')
        qtask = queue.enqueue(partial(flush, logger), 'flush')
        task.set_job_id(qtask.job_ids.pop())
