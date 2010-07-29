from Exscript.protocols.Exception import TransportException

class PostProcess(object):
    def __init__(self, provider, xml):
        processor_name = xml.get('processor')
        self.processor = provider.processors[processor_name]
        self.args      = xml.attrib
        del self.args['processor']

    def do(self, conn):
        self.processor.start(conn, **self.args)

class Authenticate(object):
    def __init__(self, provider, xml):
        self.wait = bool(xml.get('wait', True))

    def do(self, conn):
        conn.authenticate(wait = self.wait)

class AutoAuthorize(object):
    def __init__(self, provider, xml):
        self.wait = bool(xml.get('wait', True))

    def do(self, conn):
        conn.auto_authorize(wait = self.wait)

class Execute(object):
    def __init__(self, provider, xml):
        self.command      = xml.get('command')
        self.ignore_error = bool(xml.get('ignore_error', False))
        self.children     = []

        for child in xml.iterfind('post-process'):
            self.children.append(PostProcess(provider, child))

    def do(self, conn):
        conn.get_host().set('__last_command__', self.command)
        if self.ignore_error:
            try:
                conn.execute(self.command)
            except TransportException, e:
                pass
        else:
            conn.execute(self.command)
        for child in self.children:
            child.do(conn)

class Store(object):
    def __init__(self, provider, xml):
        self.filename  = xml.get('filename')
        self.filestore = provider.filestore

    def do(self, conn):
        self.filestore.store(conn, self.filename, conn.response)

class Provider(object):
    def __init__(self, xml, processors, stores):
        self.name       = xml.get('name')
        store           = xml.get('store')
        self.processors = processors
        self.store      = stores[store]
        self.tasks      = []

        for element in xml:
            if element.tag == 'authenticate':
                self.tasks.append(Authenticate(self, element))
            elif element.tag == 'auto_authorize':
                self.tasks.append(AutoAuthorize(self, element))
            elif element.tag == 'execute':
                self.tasks.append(Execute(self, element))
            elif element.tag == 'post-process':
                self.tasks.append(PostProcess(self, element))
            elif element.tag == 'store':
                self.tasks.append(Store(self, element))
            else:
                raise Exception('Invalid XML tag: %s' % element.tag)

    def start(self, conn):
        for task in self.tasks:
            task.do(conn)
