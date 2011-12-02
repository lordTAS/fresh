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
        vars = dict(os = host.get('os'), path = host.get('path'))
        vars.update(host.get_dict())
        for provider in self.providers:
            if provider.test_condition(vars):
                return provider
        raise ValueError('no matching provider found for: ' + repr(vars))

    def grab(self, exscriptd, job_id, conn, host, logger):
        # Initial log message.
        label = self.get_label_from_host(host)
        logger.info('%s: Estimating required time...' % label)

        # Prepare for progress updates.
        start = time.time()
        total = float(host.get('duration') or 60 * 10)

        def update_progress():
            """
            A callback function that updates the progress, based on the
            time it took to update the host when the service was last
            started.
            """
            time_spent = time.time() - start
            progress   = min(time_spent / total, 1.0)
            exscriptd.set_job_progress(job_id, progress)

        # Open the connection.
        logger.info('%s: Logging in...' % label)
        conn.authenticate()
        logger.info('%s: Authentication succeeded.' % label)
        update_progress()

        # Detect the operation system, and store it in the seeddb.
        os = conn.guess_os()
        logger.info('%s: Detected OS is "%s".' % (label, os))
        host.set('os', os)
        update_progress()

        # Find the provider.
        provider = self.get_provider_for_host(host)
        module   = provider.__module__
        logger.info('%s: Selected provider is %s using %s.' % (label,
                                                               provider.name,
                                                               module))

        # Init the command line.
        cfghostname = provider.get_hostname(host, conn)
        logger.info('%s: Prompt hostname is %s.' % (label, cfghostname))
        provider.init(host, conn)
        logger.info('%s: Command line initialized.' % label)
        update_progress()

        # Init default variables.
        host.set('__label__',   label)
        host.set('__logger__',  logger)
        host.set('__changed__', {})

        # Run.
        logger.info('%s: Starting.' % label)
        provider.start(host, conn, update_progress)
        logger.info('%s: Completed.' % label)
        conn.close(True)

        # Save the time it took to complete the host.
        host.set('duration', time.time() - start)
        self.save_seedhost(host)

    def flush(self, exscriptd, logger):
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
