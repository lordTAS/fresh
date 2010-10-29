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
from fresh.grabber.Config    import Config
from Exscript.util.decorator import bind

config  = Config(__service__.config_file('config.xml'))
grabber = config.get_grabber()

def run(conn, service, order, logger):
    host = conn.get_host()
    task = host.get('__task__')
    task.set_status('in-progress')
    service.save_task(order, task)

    try:
        grabber.grab(conn, service, order, logger)
    except Exception, e:
        label = grabber.get_label_from_host(host)
        logger.info('%s: Exception: %s' % (label, repr(str(e))))
        task.close('error')
        raise
    else:
        task.completed()
    finally:
        service.save_task(order, task)

def check(service, order):
    hosts = order.get_hosts()
    if not hosts:
        return False
    if len(hosts) == 1:
        order.set_description('Update ' + hosts[0].get_name())
    else:
        order.set_description('Update %d hosts' % len(hosts))
    return True

def enter(service, order):
    logger = service.create_logger(order, 'command.log')

    # Since the order only contains a list of hostnames without any
    # other info (such as the address or path), we need to load the
    # additional attributes from the database.
    hosts = []
    for host in order.get_hosts():
        task     = service.create_task(order, 'Update %s' % host.get_name())
        seedhost = grabber.get_seedhost_from_name(host.get_name())

        if not seedhost:
            hostname = host.get_name()
            logger.info('%s: Error: Address for host not found.' % hostname)
            task.close('address-not-found')
            service.save_task(order, task)
        else:
            hosts.append(seedhost)
            seedhost.set('__task__', task)

    service.enqueue_hosts(order,
                          hosts,
                          bind(run, service, order, logger),
                          handle_duplicates = True)
    service.set_order_status(order, 'queued')
