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
import os, logging, logging.handlers
from fresh.grabber.Config    import Config
from Exscript.util.decorator import bind

config  = Config(__service__.config_file('config.xml'))
grabber = config.get_grabber()

def run(conn, logger):
    try:
        grabber.grab(conn, logger)
    except Exception, e:
        logger.info('%s: Exception: %s' % (conn.get_host().get_name(), e))
        raise

def enter(service, order):
    if not order.get_hosts():
        return False
    logger   = service.create_logger(order, 'command.log')
    callback = bind(run, logger)
    service.enqueue_hosts(order, order.get_hosts(), callback)
    service.set_order_status(order, 'queued')
    return True
