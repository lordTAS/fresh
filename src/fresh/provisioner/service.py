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
import traceback
from Exscriptd.xml import get_hosts_from_etree
from Exscript.util.log import log_to_file
from fresh.provisioner.Config import Config
from functools import partial

config     = __service__.read_config('config.xml', Config)
queue_name = __service__.get_queue_name()
queue      = __exscriptd__.get_queue_from_name(queue_name)
prov       = config.get_provisioner()

def _get_script_from_xml(xml):
    # Read the script name.
    script_node = xml.find('script')
    if script_node is None:
        return None, None, None

    script_name = script_node.get('name')
    if script_name is None:
        return None, None, None

    script_type = script_node.get('type')
    if script_type == 'text/exscript':
        return 'Exscript template', script_name, script_node.text

    return None, None, None

def _get_hosts_from_xml(xml):
    host_list_node = xml.find('host-list')
    if host_list_node is None:
        return None
    return get_hosts_from_etree(host_list_node)

def check(order):
    script_type, script_name, script = _get_script_from_xml(order.xml)
    if script is None:
        return False

    hosts = _get_hosts_from_xml(order.xml)
    if not hosts:
        return False

    descr = 'Run ' + script_type + ' ' + repr(script_name)
    if len(hosts) == 1:
        order.set_description(descr + ' on ' + hosts[0].get_name())
    else:
        order.set_description(descr + ' on %d hosts' % len(hosts))
    return True

def enter(order):
    script_type, script_name, script = _get_script_from_xml(order.xml)
    if script is None:
        return False

    logger = __exscriptd__.get_logger(order, 'provisioner.log')
    hosts  = _get_hosts_from_xml(order.xml)
    if not hosts:
        logger.info('Order contains no hosts.')
        return False

    logdir = __exscriptd__.get_order_logdir(order)
    descr = 'Run ' + script_type + ' ' + repr(script_name)
    @log_to_file(logdir)
    def start(*args, **kwargs):
        try:
            return prov.run(script, *args, **kwargs)
        except Exception:
            logger.error(traceback.format_exc())
            raise
    for host in hosts:
        # Track the status of the update per-host.
        hostname = host.get_name()
        msg      = descr + ' on ' + hostname
        task     = __exscriptd__.create_task(order, msg)
        task.set_logfile(logdir, hostname + '.log')

        # Since the order only contains a list of hostnames without any
        # other info (such as static passwords), we need to load the
        # additional attributes from the database.
        seedhost = prov.get_seedhost_from_name(hostname)
        if not seedhost:
            logger.info('%s: Error: Address for host not found.' % hostname)
            task.close('address-not-found')
            continue

        # Enqueue the host.
        qtask  = queue.run(seedhost, start)

        # Associate the queued job with the task such that Exscriptd can
        # update the status of the task.
        job_id = qtask.job_ids.pop()
        task.set_job_id(job_id)
        logger.info('%s: Queued with job id %s.' % (hostname, job_id))
