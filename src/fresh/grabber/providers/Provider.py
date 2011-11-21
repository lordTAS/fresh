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
import logging
from lxml import etree
from Exscript.protocols.Exception import ProtocolException

class Action(object):
    def do(self, host, conn):
        raise NotImplementedError()

    def cleanup(self, host):
        pass

    def hlog(self, host, msg, level = logging.INFO):
        label  = host.get('__label__')
        logger = host.get('__logger__')
        logger.log(level, label + ': ' + msg)

    def log(self, host, msg, level = logging.INFO):
        self.hlog(host, msg, level)

    def dbg(self, host, msg):
        self.log(host, msg, logging.DEBUG)

class PostProcess(Action):
    def __init__(self, provider, xml):
        self.processor_name = xml.get('processor')
        self.provider       = provider
        self.processor      = provider.processors[self.processor_name]
        self.args           = xml.attrib
        del self.args['processor']

    def do(self, host, conn):
        name = repr(self.processor_name)
        args = repr(self.args)
        self.dbg(host, 'running post-processor %s with args %s' % (name, args))
        self.processor.start(self.provider, host, conn, **self.args)

    def cleanup(self, host):
        name = repr(self.processor_name)
        args = repr(self.args)
        self.hlog(host, 'running %s.delete() with args %s' % (name, args))
        self.processor.delete(self.provider, host, **self.args)

class Login(Action):
    def __init__(self, provider, xml):
        self.flush = bool(xml.get('flush', True))

    def do(self, host, conn):
        conn.login(flush = self.flush)

class Authenticate(Action):
    def __init__(self, provider, xml):
        self.flush = bool(xml.get('flush', True))

    def do(self, host, conn):
        conn.authenticate(flush = self.flush)

class ProtocolAuthenticate(Action):
    def __init__(self, provider, xml):
        pass

    def do(self, host, conn):
        conn.protocol_authenticate()

class AppAuthenticate(Action):
    def __init__(self, provider, xml):
        self.flush = bool(xml.get('flush', True))

    def do(self, host, conn):
        conn.app_authenticate(flush = self.flush)

class AppAuthorize(Action):
    def __init__(self, provider, xml):
        self.flush = bool(xml.get('flush', True))

    def do(self, host, conn):
        conn.app_authorize(flush = self.flush)

class AutoAppAuthorize(Action):
    def __init__(self, provider, xml):
        self.flush = bool(xml.get('flush', True))

    def do(self, host, conn):
        conn.auto_app_authorize(flush = self.flush)

class Store(Action):
    def __init__(self, provider, xml):
        self.provider  = provider
        self.filename  = xml.get('filename')
        self.alias     = xml.get('alias')
        self.versions  = int(xml.get('versions', 1))
        self.store     = provider.store
        self.cleanpass = bool(int(xml.get('remove-passwords',    False)))
        self.cleandesc = bool(int(xml.get('remove-descriptions', False)))

    def do(self, host, conn):
        self.store.store(self.provider,
                         host,
                         self.filename,
                         conn.response,
                         alias     = self.alias,
                         versions  = self.versions,
                         cleanpass = self.cleanpass,
                         cleandesc = self.cleandesc)

    def cleanup(self, host):
        self.store.delete(host)

class Execute(Action):
    def __init__(self, provider, xml):
        self.command  = xml.get('command')
        self.on_error = xml.get('on_error', 'raise')
        self.children = []
        self.timeout  = xml.get('timeout')
        if self.timeout is not None:
            self.timeout = int(self.timeout)

        if self.on_error not in ('skip', 'continue', 'raise'):
            raise TypeError('Invalid value for on_error: %s' % self.on_error)

        for child in xml:
            if child.tag == 'post-process':
                self.children.append(PostProcess(provider, child))
            elif child.tag == 'store':
                self.children.append(Store(provider, child))
            else:
                raise Exception('Invalid XML tag: %s' % element.tag)

    def do(self, host, conn):
        cmd  = repr(self.command)
        host.set('__last_command__', self.command)
        self.log(host, 'Executing %s' % repr(cmd))

        old_timeout = conn.get_timeout()
        if self.timeout is not None:
            conn.set_timeout(self.timeout)

        try:
            conn.execute(self.command)
        except ProtocolException, e:
            err = repr(str(e))
            if self.on_error == 'skip':
                self.log(host, '%s during %s, skipping' % (err, cmd))
                return
            elif self.on_error == 'continue':
                self.log(host, '%s during %s, handling anyway' % (err, cmd))
            elif self.on_error == 'raise':
                self.log(host, 'Exception %s during %s' % (err, cmd))
                raise
            else:
                raise Exception('BUG: on_error is %s' % self.on_error)
        else:
            self.log(host, 'Command succeeded: %s' % cmd)
        finally:
            conn.set_timeout(old_timeout)

        for child in self.children:
            child.do(host, conn)

    def cleanup(self, host):
        for child in self.children:
            child.cleanup(host)

class Provider(object):
    def __init__(self, xml, processors, stores):
        self.name       = xml.get('name')
        store           = xml.get('store')
        self.condition  = None
        self.processors = processors
        self.store      = stores[store]
        self.tasks      = []

        for element in xml:
            if element.tag == 'login':
                self.tasks.append(Login(self, element))
            elif element.tag == 'authenticate':
                self.tasks.append(Authenticate(self, element))
            elif element.tag == 'protocol-authenticate':
                self.tasks.append(ProtocolAuthenticate(self, element))
            elif element.tag == 'app-authenticate':
                self.tasks.append(AppAuthenticate(self, element))
            elif element.tag == 'app-authorize':
                self.tasks.append(AppAuthorize(self, element))
            elif element.tag == 'auto-app-authorize':
                self.tasks.append(AutoAppAuthorize(self, element))
            elif element.tag == 'execute':
                self.tasks.append(Execute(self, element))
            elif element.tag == 'post-process':
                self.tasks.append(PostProcess(self, element))
            elif element.tag is etree.Comment:
                pass
            else:
                raise Exception('Invalid XML tag: %s' % element.tag)

    def set_condition(self, cond):
        self.condition = compile(cond, 'config', 'eval')

    def test_condition(self, vars):
        if not self.condition:
            return True
        return eval(self.condition, vars.copy())

    def get_store(self):
        return self.store

    def start(self, host, conn, update_progress_func):
        for task in self.tasks:
            task.do(host, conn)
            update_progress_func()

    def delete(self, host):
        for task in self.tasks:
            task.cleanup(host)
