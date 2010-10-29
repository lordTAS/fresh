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

class Grabber(object):
    def __init__(self, seeddb, processors, providers):
        self.seeddb     = seeddb
        self.processors = processors
        self.providers  = providers

    def get_seedhost_from_name(self, name):
        return self.seeddb.get_host(name = name)

    def save_seedhost(self, host):
        self.seeddb.save_host(host)

    def get_label_from_host(self, host):
        return host.get_address() + '/' + host.get_name()

    def grab(self, conn, service, order, logger):
        # Initial log message.
        host  = conn.get_host()
        task  = host.get('__task__')
        label = self.get_label_from_host(host)
        logger.info('%s: Connecting...' % label)

        # Open the connection.
        conn.open()
        conn.authenticate(wait = True)
        logger.info('%s: Authentication succeeded.' % label)

        # Detect the operation system, and store it in the seeddb.
        os = conn.guess_os()
        logger.info('%s: Detected OS is "%s".' % (label, os))
        host.set('os', os)
        self.save_seedhost(host)

        # Find and init the provider.
        provider    = self.providers.get(os)
        cfghostname = provider.get_hostname(conn)
        logger.info('%s: Prompt hostname is %s.' % (label, cfghostname))
        if provider is None:
            logger.info('%s: Detected OS is not supported.' % label)
            raise Exception('Error: No provider for %s found.' % repr(os))
        logger.info('%s: Initializing command line.' % label)
        provider.init(conn)

        # Init default variables.
        host.set('__path__',   host.get('path'))
        host.set('__label__',  label)
        host.set('__logger__', logger)

        # Run.
        logger.info('%s: Starting.' % label)
        provider.start(conn)
        logger.info('%s: Completed.' % label)
