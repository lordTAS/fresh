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
from functools               import partial
from Exscriptd.xml           import get_hosts_from_etree
from fresh.grabber.Config    import Config
from Exscript.util.decorator import bind

config  = __service__.config('config.xml', Config)
grabber = config.get_grabber()

def run(conn, order, logger):
    host = conn.get_host()
    task = host.get('__task__')
    task.set_logfile(host.get_logname() + '.log')
    task.set_tracefile(host.get_logname() + '.log.error')
    task.set_status('in-progress')
    __service__.save_task(order, task)

    try:
        grabber.grab(conn, __service__, order, logger)
    except Exception, e:
        label = grabber.get_label_from_host(host)
        logger.info('%s: Exception: %s' % (label, repr(str(e))))
        task.close('error')
        raise
    else:
        task.completed()
    finally:
        __service__.save_task(order, task)

def flush(order, task, logger):
    task.set_logfile('flush.log')
    task.set_tracefile('flush.log.error')
    task.set_status('in-progress')
    __service__.save_task(order, task)

    try:
        grabber.flush(__service__, order, logger)
    except Exception, e:
        logger.info('flush: Exception: %s' % repr(str(e)))
        task.close('error')
        raise
    else:
        task.completed()
    finally:
        __service__.save_task(order, task)

def check(order):
    hosts = get_hosts_from_etree(order.xml)

    if not hosts:
        descr = ''
    elif len(hosts) == 1:
        descr = 'Update ' + hosts[0].get_name()
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
    logger = __service__.create_logger(order, 'command.log')

    # Since the order only contains a list of hostnames without any
    # other info (such as the address or path), we need to load the
    # additional attributes from the database.
    hosts = []
    for host in get_hosts_from_etree(order.xml):
        task     = __service__.create_task(order, 'Update %s' % host.get_name())
        seedhost = grabber.get_seedhost_from_name(host.get_name())

        if not seedhost:
            hostname = host.get_name()
            logger.info('%s: Error: Address for host not found.' % hostname)
            task.close('address-not-found')
            __service__.save_task(order, task)
        else:
            hosts.append(seedhost)
            seedhost.set('__task__', task)

    __service__.enqueue_hosts(order,
                              hosts,
                              bind(run, order, logger),
                              handle_duplicates = True)

    if order.xml.find('flush') is not None:
        task = __service__.create_task(order, 'Delete obsolete hosts')
        __service__.enqueue(order,
                            partial(flush, order, task, logger),
                            'flush')

    __service__.set_order_status(order, 'queued')
    return True
