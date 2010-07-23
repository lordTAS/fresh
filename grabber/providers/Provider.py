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
        wait      = xml.get('wait')
        self.wait = wait is None and True or bool(wait)

    def do(self, conn):
        conn.authenticate(wait = self.wait)

class AutoAuthorize(object):
    def __init__(self, provider, xml):
        wait      = xml.get('wait')
        self.wait = wait is None and True or bool(wait)

    def do(self, conn):
        conn.auto_authorize(wait = self.wait)

class Execute(object):
    def __init__(self, provider, xml):
        self.command  = xml.get('command')
        self.children = []

        for child in xml.iterfind('post-process'):
            self.children.append(PostProcess(provider, child))

    def do(self, conn):
        conn.execute(self.command)
        conn.get_host().set('__last_command__', self.command)
        for child in self.children:
            child.do(conn)

class Provider(object):
    def __init__(self, xml, processors):
        self.name       = xml.get('name')
        self.processors = processors
        self.tasks      = []

        for element in xml:
            if element.tag == 'authenticate':
                self.tasks.append(Authenticate(self, element))
            elif element.tag == 'auto_authorize':
                self.tasks.append(AutoAuthorize(self, element))
            elif element.tag == 'execute':
                self.tasks.append(Execute(self, element))

    def start(self, conn):
        for task in self.tasks:
            task.do(conn)
