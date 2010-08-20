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

    def get_path_from_address(self, address):
        host = self.seeddb.get_host(address = address)
        if not host:
            raise Exception('unknown host: %s' % address)
        return host.get('path')

    def grab(self, conn, logger, label):
        logger.info('%s: Connecting...' % label)

        # Open the connection.
        conn.open()
        conn.authenticate(wait = True)
        logger.info('%s: Authentication succeeded.' % label)

        # Detect the operation system.
        os = conn.guess_os()
        logger.info('%s: Detected OS is "%s".' % (label, os))

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
        host    = conn.get_host()
        address = host.get_address()
        host.set('__path__',          self.get_path_from_address(address))
        host.set('__real_hostname__', hostname or host.get_name())
        host.set('__label__',         label)
        host.set('__logger__',        logger)

        # Run.
        logger.info('%s: Starting.' % label)
        provider.start(conn)
        logger.info('%s: Completed.' % label)
