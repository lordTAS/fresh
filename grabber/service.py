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
        host    = conn.get_host()
        address = host.get_address()
        logger.info('%s: Exception: %s' % (address, repr(str(e))))
        raise

def check(service, order):
    return order.get_hosts() and True or False

def enter(service, order):
    logger   = service.create_logger(order, 'command.log')
    callback = bind(run, logger)
    service.enqueue_hosts(order,
                          order.get_hosts(),
                          callback,
                          handle_duplicates = True)
    service.set_order_status(order, 'queued')
