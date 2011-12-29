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
import os, re, imp
from sqlalchemy        import create_engine
from fresh.seed.Config import get_seeddb_from_name
from lxml              import etree
from pyexist           import ExistDB
from Exscriptd         import ConfigReader
from Grabber           import Grabber
from FileStore         import FileStore
from processors        import GelatinProcessor, \
                              LineSplitProcessor, \
                              XsltProcessor,    \
                              ExistDBStore,     \
                              ExistDBMetadataStore

__dirname__ = os.path.dirname(__file__)

class Config(ConfigReader):
    def __init__(self, filename, parent):
        ConfigReader.__init__(self, filename, parent = parent)
        self.stores     = {}
        self.processors = {}
        self.exist_dbs  = {}
        self.grabber    = None
        self._init()

    def _init_file_stores(self):
        for element in self.cfgtree.iterfind('file-store'):
            name    = element.get('name')
            basedir = element.find('basedir').text
            #print 'Creating file store "%s".' % name
            self.stores[name] = FileStore(basedir)

    def _init_linesplit(self):
        for element in self.cfgtree.iterfind('processor[@type="linesplit"]'):
            name = element.get('name')
            self.processors[name] = LineSplitProcessor()

    def _init_gelatin(self):
        for element in self.cfgtree.iterfind('processor[@type="gelatin"]'):
            name       = element.get('name')
            syntax_dir = element.find('syntax-dir').text
            format     = element.find('format').text
            if not syntax_dir.startswith('/'):
                syntax_dir = os.path.join(__dirname__, syntax_dir)
            #print 'Creating Gelatin processor "%s".' % name
            self.processors[name] = GelatinProcessor(syntax_dir, format)

    def _init_invoke_module(self):
        for element in self.cfgtree.iterfind('processor[@type="invoke-module"]'):
            name        = element.get('name')
            module_name = element.find('module').text
            self.processors[name] = InvokeModule(module_name)

    def _init_xsltproc(self):
        for element in self.cfgtree.iterfind('processor[@type="xslt"]'):
            name      = element.get('name')
            xsl_dir   = element.find('xsl-dir').text
            hostname  = element.find('add-hostname') is not None
            address   = element.find('add-address') is not None
            timestamp = element.find('add-timestamp') is not None
            if not xsl_dir.startswith('/'):
                xsl_dir = os.path.join(__dirname__, xsl_dir)
            #print 'Creating XSLT processor "%s".' % name
            self.processors[name] = XsltProcessor(xsl_dir,
                                                  hostname,
                                                  address,
                                                  timestamp)

    def init_existdb_from_name(self, name):
        if self.exist_dbs.has_key(name):
            return self.exist_dbs[name]
        element    = self.cfgtree.find('exist-db[@name="%s"]' % name)
        host       = element.find('host').text
        port       = element.find('port').text
        user       = element.find('user').text
        password   = element.find('password').text
        path       = element.find('path').text
        collection = element.find('collection').text
        netloc     = user + ':' + password + '@' + host + ':' + port
        db         = ExistDB(netloc + '/' + path, collection)
        self.exist_dbs['name'] = db
        return db

    def _init_xmldb_store(self):
        path = 'processor[@type="xml-db-store"]'
        for element in self.cfgtree.iterfind(path):
            name   = element.get('name')
            dbname = element.find('xml-db').text
            db     = self.init_existdb_from_name(dbname)
            self.processors[name] = ExistDBStore(db)

    def _init_xmldb_metadata(self):
        path = 'processor[@type="xml-db-metadata"]'
        for element in self.cfgtree.iterfind(path):
            name   = element.get('name')
            dbname = element.find('xml-db').text
            db     = self.init_existdb_from_name(dbname)
            self.processors[name] = ExistDBMetadataStore(db)

    def _init_provider_from_name(self, name):
        element = self.cfgtree.find('provider[@name="%s"]' % name)
        modname = element.get('module')
        #print 'Loading provider "%s" (%s).' % (name, modname)
        themodule = __import__(modname, fromlist = [modname])
        theclass  = themodule.provider
        return theclass(element, self.processors, self.stores)

    def _init(self):
        self._init_file_stores()
        self._init_linesplit()
        self._init_gelatin()
        self._init_xsltproc()
        self._init_invoke_module()
        self._init_xmldb_store()
        self._init_xmldb_metadata()

        grabber_elem = self.cfgtree.find('grabber')
        seeddb_name  = grabber_elem.find('seeddb').text
        seeddb       = get_seeddb_from_name(self, seeddb_name)
        providers    = []
        for provider_elem in grabber_elem.iterfind('provider'):
            provider_name = provider_elem.text
            provider      = self._init_provider_from_name(provider_name)
            cond          = provider_elem.get('if')
            if cond is not None:
                provider.set_condition(cond)
            providers.append(provider)

        self.grabber = Grabber(seeddb,
                               self.processors,
                               self.stores,
                               providers)

    def get_grabber(self):
        return self.grabber
