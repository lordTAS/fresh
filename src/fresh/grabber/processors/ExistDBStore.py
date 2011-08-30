# Copyright (C) 2007-2011 Samuel Abels.
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
from hashlib import md5
from Processor import Processor
from lxml import etree

class ExistDBStore(Processor):
    def __init__(self, db):
        self.db = db

    def _replace_vars(self, host, string):
        if string is None:
            return None
        address  = host.get_address()
        hostname = host.get_name()
        string   = string.replace('{address}',  address)
        string   = string.replace('{hostname}', hostname)
        return string

    def _txt2xml(self, hostname, content):
        ts  = time.asctime()
        xml = etree.Element('xml', hostname = hostname, timestamp = ts)
        for n, line in enumerate(content.split('\n')):
            line = unicode(line, 'latin-1')
            etree.SubElement(xml, 'line', number = str(n + 1)).text = line
        return xml

    def _move_to_history(self, document, collection):
        xquery = '''
        if (doc-available('%{document}'))
        then
            let $cstatus   := xmldb:create-collection('%{context}', '%{destination}')
            let $abssource := '/%{context}/%{path}'
            let $absdest   := '/%{context}/%{destination}'
            let $mstatus   := xmldb:move($abssource, $absdest, '%{basename}')
            return <status>{$mstatus}</status>
        else ()
        '''

        path, basename = document.rsplit('/', 1)
        query = self.db.query(xquery,
                              context     = self.db.collection,
                              document    = document,
                              path        = path,
                              basename    = basename,
                              destination = collection)
        return query.execute()

    def _hash_equals(self, document, hash):
        xquery = '''
        if (empty(doc('%{document}')/*[@hash='%{hash}']))
        then <status>not-found</status>
        else <status>found</status>
        '''
        try:
            collection, resource = document.rsplit('/', 1)
        except ValueError:
            collection = ''
            resource   = document
        query = self.db.query(xquery,
                              document = document,
                              resource = resource,
                              hash     = hash)
        result = query.execute().findtext('status')
        return result == 'found'

    def _rename_if_exists(self, document, new_name):
        xquery = '''
        if (doc-available('%{document}'))
        then
            let $status := xmldb:rename('/%{context}/%{collection}',
                                        '%{resource}',
                                        '%{newname}')
            return <status>{$status}</status>
        else ()
        '''
        try:
            collection, resource = document.rsplit('/', 1)
        except ValueError:
            collection = ''
            resource   = document
        query = self.db.query(xquery,
                              context    = self.db.collection,
                              document   = document,
                              collection = collection,
                              resource   = resource,
                              newname    = new_name)
        query.execute()
        return query

    def _delete_if_exists(self, document):
        xquery = '''
        if (doc-available('%{document}'))
        then
            let $status := xmldb:remove('/%{context}/%{collection}',
                                        '%{resource}')
            return <status>{$status}</status>
        else ()
        '''
        try:
            collection, resource = document.rsplit('/', 1)
        except ValueError:
            collection = ''
            resource   = document
        query = self.db.query(xquery,
                              context    = self.db.collection,
                              document   = document,
                              collection = collection,
                              resource   = resource)
        query.execute()
        return query

    def _push(self, document, collection, versions):
        # Move the given document to the given history collection.
        # Note that XQuery provides no API for moving a document and renaming
        # it at the same time, so we append the sequence number to the
        # document name later.
        self._move_to_history(document, collection)

        # Documents in the history have a sequence number appended.
        # Increase this sequence number for each version, and delete
        # the one with the highest sequence number.
        basename = document.split('/')[-1]
        pathname = collection + '/' + basename
        for version in range(versions, -1, -1):
            if version == 0:
                source = pathname
            else:
                source = pathname + '.' + str(version)
            if version == versions:
                self._delete_if_exists(source)
                continue
            destination = basename + '.' + str(version + 1)
            self._rename_if_exists(source, destination)

    def start(self, provider, host, conn, **kwargs):
        filename = kwargs.get('filename')
        document = kwargs.get('document')
        document = self._replace_vars(host, document)
        history  = kwargs.get('history')
        history  = self._replace_vars(host, history)
        versions = int(kwargs.get('versions', 1))
        content  = provider.store.get(host, filename)
        hash     = md5(content).hexdigest()

        if self._hash_equals(document, hash):
            return

        # Read the file, and parse it into a DOM.
        if filename.endswith('.txt'):
            content = self._txt2xml(host.get_name(), content)
        else:
            content = etree.fromstring(content)
        content.attrib['hash'] = hash

        # If requested, store the last version of the document in the history.
        if history:
            self._push(document, history, versions)
        self.db.store(document, content)

    def delete(self, provider, host, **kwargs):
        label    = host.get('__label__')
        logger   = host.get('__logger__')
        document = kwargs.get('document')
        document = self._replace_vars(host, document)
        try:
            self.db.delete(document)
        except Exception, e:
            logger.error('%s: error during delete: %s' % (label, str(e)))
        else:
            logger.info('%s: deleted %s' % (label, document))
