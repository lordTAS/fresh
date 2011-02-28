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
import time
from itertools import chain

class Grabber(object):
    def __init__(self, seeddb, processors, stores, providers):
        self.seeddb     = seeddb
        self.processors = processors
        self.stores     = stores
        self.providers  = providers

    def get_seedhost_from_name(self, name):
        return self.seeddb.get_host(name = name)

    def save_seedhost(self, host):
        self.seeddb.save_host(host)

    def get_label_from_host(self, host):
        return host.get_name() \
             + ' (' \
                 + host.get_protocol() \
                 + '://' + host.get_address() \
                 + ':' + str(host.get_tcp_port()) \
             + ')'

    def get_provider_for_host(self, host):
        vars = dict(os       = host.get('os'),
                    hostname = host.get_name(),
                    address  = host.get_address(),
                    path     = host.get('path'))
        for provider in self.providers:
            if provider.test_condition(vars):
                return provider
        raise ValueError('no matching provider found for: ' + repr(vars))

    def grab(self, conn, service, order, logger):
        # Initial log message.
        host  = conn.get_host()
        label = self.get_label_from_host(host)
        logger.info('%s: Estimating required time...' % label)

        # Prepare for progress updates.
        start = time.time()
        task  = host.get('__task__')
        total = float(host.get('duration') or 60 * 10)

        def update_progress():
            """
            A callback function that updates the progress, based on the
            time it took to update the host when the service was last
            started.
            """
            time_spent = time.time() - start
            task.set_progress(min(time_spent / total, 1.0))
            service.save_task(order, task)

        # Open the connection.
        logger.info('%s: Connecting...' % label)
        conn.connect()
        conn.login()
        logger.info('%s: Authentication succeeded.' % label)
        update_progress()

        # Detect the operation system, and store it in the seeddb.
        os = conn.guess_os()
        logger.info('%s: Detected OS is "%s".' % (label, os))
        host.set('os', os)
        update_progress()

        # Find the provider.
        provider = self.get_provider_for_host(host)
        logger.info('%s: Selected provider is %s.' % (label, provider.name))

        # Init the command line.
        cfghostname = provider.get_hostname(conn)
        logger.info('%s: Prompt hostname is %s.' % (label, cfghostname))
        provider.init(conn)
        logger.info('%s: Command line initialized.' % label)
        update_progress()

        # Init default variables.
        host.set('__path__',   host.get('path'))
        host.set('__label__',  label)
        host.set('__logger__', logger)

        # Run.
        logger.info('%s: Starting.' % label)
        provider.start(conn, update_progress)
        logger.info('%s: Completed.' % label)
        conn.close(True)

        # Save the time it took to complete the host.
        host.set('duration', time.time() - start)
        self.save_seedhost(host)

    def flush(self, service, order, logger):
        # Pass each deleted host to it's provider to clean up the data.
        for host in self.seeddb.get_hosts(deleted = True):
            label = self.get_label_from_host(host)
            logger.info(label + ': found dead')
            host.set('__label__',  label)
            host.set('__logger__', logger)

            try:
                provider = self.get_provider_for_host(host)
            except ValueError:
                logger.info(label + ': no provider found, cleanup skipped')
                continue
            provider.delete(host)

        # Now drop the obsolete hosts from the seed database.
        self.seeddb.delete_host(deleted = True)
