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
from Exscriptd.xml import get_hosts_from_etree
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

    hosts = _get_hosts_from_xml(order.xml)
    if not hosts:
        return False

    descr = 'Run ' + script_type + ' ' + repr(script_name)
    start = partial(prov.run, script)
    for host in hosts:
        msg  = descr + ' on ' + host.get_name()
        task = __exscriptd__.create_task(order, msg)
        task.set_logfile(host.get_name() + '.log')
        qtask = queue.run(partial(run, order, script), 'packager')
        task.set_job_id(qtask.job_ids.pop())
