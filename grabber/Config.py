#!/usr/bin/env python
import os, base64, re, imp
from sqlalchemy     import create_engine
from fresh.seed     import HostDB
from lxml           import etree
from Exscriptd.util import resolve_variables
from Grabber        import Grabber
from FileStore      import FileStore
from processors     import GelatinProcessor, XsltProcessor, ExistDBStore

__dirname__ = os.path.dirname(__file__)

class Config(object):
    def __init__(self, filename):
        self.cfgtree    = etree.parse(filename)
        self.variables  = {}
        self.providers  = {}
        self.stores     = {}
        self.processors = {}
        self.grabber    = None
        self._clean_tree()
        self._init()

    def _resolve(self, text):
        if text is None:
            return None
        return resolve_variables(self.variables, text.strip())

    def _clean_tree(self):
        # Read all variables.
        for element in self.cfgtree.find('variables'):
            varname = element.tag.strip()
            value   = resolve_variables(self.variables, element.text)
            self.variables[varname] = value

        # Resolve variables everywhere.
        for element in self.cfgtree.iter():
            element.text = self._resolve(element.text)
            for attr in element.attrib:
                value                = element.attrib[attr]
                element.attrib[attr] = self._resolve(value)

    def init_database_from_name(self, name):
        element = self.cfgtree.find('database[@name="%s"]' % name)
        dbn     = element.find('dbn').text
        print 'Creating database connection for', dbn
        engine  = create_engine(dbn)
        return HostDB(engine)

    def _init_file_stores(self):
        for element in self.cfgtree.iterfind('file-store'):
            name    = element.get('name')
            basedir = element.find('basedir').text
            print 'Creating file store "%s".' % name
            self.stores[name] = FileStore(basedir)

    def _init_gelatin(self):
        for element in self.cfgtree.iterfind('processor[@type="gelatin"]'):
            name       = element.get('name')
            syntax_dir = element.find('syntax-dir').text
            format     = element.find('format').text
            if not syntax_dir.startswith('/'):
                syntax_dir = os.path.join(__dirname__, syntax_dir)
            print 'Creating Gelatin processor "%s".' % name
            self.processors[name] = GelatinProcessor(syntax_dir, format)

    def _init_xsltproc(self):
        for element in self.cfgtree.iterfind('processor[@type="xslt"]'):
            name      = element.get('name')
            xsl_dir   = element.find('xsl-dir').text
            timestamp = element.find('add-timestamp') is not None
            if not xsl_dir.startswith('/'):
                xsl_dir = os.path.join(__dirname__, xsl_dir)
            print 'Creating XSLT processor "%s".' % name
            self.processors[name] = XsltProcessor(xsl_dir, timestamp)

    def _init_existdb(self):
        for element in self.cfgtree.iterfind('processor[@type="exist-db"]'):
            name       = element.get('name')
            host       = element.find('host').text
            port       = element.find('port').text
            user       = element.find('user').text
            password   = element.find('password').text
            collection = element.find('collection').text
            print 'Creating eXist-db processor "%s".' % name
            self.processors[name] = ExistDBStore(host,
                                                 port,
                                                 user,
                                                 password,
                                                 collection)

    def _init_providers(self):
        for element in self.cfgtree.iterfind('provider'):
            name     = element.get('name')
            filename = element.get('filename')
            basename = os.path.basename(filename)
            modname  = os.path.splitext(basename)[0]
            if not filename.startswith('/'):
                filename = os.path.join(__dirname__, filename)

            print 'Loading provider "%s" (%s).' % (name, modname)
            themodule            = imp.load_source(modname, filename)
            theclass             = getattr(themodule, modname)
            self.providers[name] = theclass(element,
                                            self.processors,
                                            self.stores)

    def _init(self):
        self._init_file_stores()
        self._init_gelatin()
        self._init_xsltproc()
        self._init_existdb()
        self._init_providers()
        element      = self.cfgtree.find('grabber')
        seeddb_name  = element.find('seeddb').text
        seeddb       = self.init_database_from_name(seeddb_name)
        self.grabber = Grabber(seeddb, self.processors, self.providers)

    def get_grabber(self):
        return self.grabber
