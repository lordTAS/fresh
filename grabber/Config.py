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
import os, base64, re, imp
from sqlalchemy import create_engine
from fresh.seed import HostDB
from lxml       import etree
from pyexist    import ExistDB
from Exscriptd  import ConfigReader
from Grabber    import Grabber
from FileStore  import FileStore
from processors import GelatinProcessor, XsltProcessor, ExistDBStore

__dirname__ = os.path.dirname(__file__)

class Config(ConfigReader):
    def __init__(self, filename):
        ConfigReader.__init__(self, filename)
        self.providers  = {}
        self.stores     = {}
        self.processors = {}
        self.exist_dbs  = {}
        self.grabber    = None
        self._init()

    def init_database_from_name(self, name):
        element = self.cfgtree.find('database[@name="%s"]' % name)
        dbn     = element.find('dbn').text
        #print 'Creating database connection for', dbn
        engine  = create_engine(dbn)
        return HostDB(engine)

    def _init_file_stores(self):
        for element in self.cfgtree.iterfind('file-store'):
            name    = element.get('name')
            basedir = element.find('basedir').text
            #print 'Creating file store "%s".' % name
            self.stores[name] = FileStore(basedir)

    def _init_gelatin(self):
        for element in self.cfgtree.iterfind('processor[@type="gelatin"]'):
            name       = element.get('name')
            syntax_dir = element.find('syntax-dir').text
            format     = element.find('format').text
            if not syntax_dir.startswith('/'):
                syntax_dir = os.path.join(__dirname__, syntax_dir)
            #print 'Creating Gelatin processor "%s".' % name
            self.processors[name] = GelatinProcessor(syntax_dir, format)

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
        collection = element.find('collection').text
        uri        = user + ':' + password + '@' + host + ':' + port
        db         = ExistDB(uri, collection)
        self.exist_dbs['name'] = db
        return db

    def _init_xmldb_store(self):
        path = 'processor[@type="xml-db-store"]'
        for element in self.cfgtree.iterfind(path):
            name   = element.get('name')
            dbname = element.find('xml-db').text
            db     = self.init_existdb_from_name(dbname)
            self.processors[name] = ExistDBStore(db)

    def _init_providers(self):
        for element in self.cfgtree.iterfind('provider'):
            name     = element.get('name')
            filename = element.get('filename')
            basename = os.path.basename(filename)
            modname  = os.path.splitext(basename)[0]
            if not filename.startswith('/'):
                filename = os.path.join(__dirname__, filename)

            #print 'Loading provider "%s" (%s).' % (name, modname)
            themodule            = imp.load_source(modname, filename)
            theclass             = getattr(themodule, modname)
            self.providers[name] = theclass(element,
                                            self.processors,
                                            self.stores)

    def _init(self):
        self._init_file_stores()
        self._init_gelatin()
        self._init_xsltproc()
        self._init_xmldb_store()
        self._init_providers()
        element      = self.cfgtree.find('grabber')
        seeddb_name  = element.find('seeddb').text
        seeddb       = self.init_database_from_name(seeddb_name)
        self.grabber = Grabber(seeddb, self.processors, self.providers)

    def get_grabber(self):
        return self.grabber
