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

def run(conn, logger):
    try:
        grabber.grab(conn, logger)
    except Exception, e:
        host  = conn.get_host()
        label = grabber.get_label_from_host(host)
        logger.info('%s: Exception: %s' % (label, repr(str(e))))
        raise

def check(service, order):
    return order.get_hosts() and True or False

def enter(service, order):
    logger = service.create_logger(order, 'command.log')

    # Since the order only contains a list of hostnames without any
    # other info (such as the address or path), we need to load the
    # additional attributes from the database.
    hosts = []
    for host in order.get_hosts():
        seedhost = grabber.get_seedhost_from_name(host.get_name())
        if not seedhost:
            hostname = host.get_name()
            logger.info('%s: Error: Address for host not found.' % hostname)
        else:
            hosts.append(seedhost)

    service.enqueue_hosts(order,
                          hosts,
                          bind(run, logger),
                          handle_duplicates = True)
    service.set_order_status(order, 'queued')
