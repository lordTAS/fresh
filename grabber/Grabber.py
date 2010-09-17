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

    def get_seedhost_from_address(self, address):
        host = self.seeddb.get_host(address = address)
        if not host:
            raise Exception('unknown host: %s' % address)
        return host

    def save_seedhost(self, host):
        self.seeddb.save_host(host)

    def get_label_from_host(self, host):
        address = host.get_address()
        alias   = host.get('alias')
        label   = address + '/' + alias
        return label

    def grab(self, conn, logger):
        # Since the order only contains the list of hosts without any
        # other info (such as the alias or path), we need to load the
        # additional attributes from the database.
        host      = conn.get_host()
        address   = host.get_address()
        seedhost  = self.get_seedhost_from_address(address)

        # Initial log message.
        label = self.get_label_from_host(seedhost)
        logger.info('%s: Connecting...' % label)

        # Open the connection.
        conn.open()
        conn.authenticate(wait = True)
        logger.info('%s: Authentication succeeded.' % label)

        # Detect the operation system, and store it in the seeddb.
        os = conn.guess_os()
        logger.info('%s: Detected OS is "%s".' % (label, os))
        seedhost.set('os', os)
        self.save_seedhost(seedhost)

        # Find and init the provider.
        provider = self.providers.get(os)
        hostname = provider.get_hostname(conn)
        logger.info('%s: Prompt hostname is %s.' % (label, hostname))
        if provider is None:
            logger.info('%s: Detected OS is not supported.' % label)
            raise Exception('Error: No provider for %s found.' % repr(os))
        logger.info('%s: Initializing command line.' % label)
        provider.init(conn)

        # Init default variables.
        host.set('__alias__',         seedhost.get('alias'))
        host.set('__path__',          seedhost.get('path'))
        host.set('__real_hostname__', hostname or host.get_name())
        host.set('__label__',         label)
        host.set('__logger__',        logger)

        # Run.
        logger.info('%s: Starting.' % label)
        provider.start(conn)
        logger.info('%s: Completed.' % label)
