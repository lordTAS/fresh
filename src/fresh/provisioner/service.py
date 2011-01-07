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
from Exscriptd.xml            import get_hosts_from_etree
from fresh.provisioner.Config import Config
from Exscript.util.decorator  import bind

config = __service__.config('config.xml', Config)
prov   = config.get_provisioner()

def run(conn, order, script):
    host = conn.get_host()
    task = host.get('__task__')
    del host.vars['__task__']
    task.set_logfile(host.get_logname() + '.log')
    task.set_tracefile(host.get_logname() + '.log.error')
    task.set_status('in-progress')
    __service__.save_task(order, task)

    try:
        prov.run(conn, __service__, order, host, script)
    except Exception, e:
        task.close('error')
        raise
    else:
        task.completed()
    finally:
        __service__.save_task(order, task)

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
    for host in hosts:
        task = __service__.create_task(order, descr + ' on ' + host.get_name())
        host.set('__task__', task)

    __service__.enqueue_hosts(order,
                              hosts,
                              bind(run, order, script),
                              handle_duplicates = True)
    __service__.set_order_status(order, 'queued')
    return True
