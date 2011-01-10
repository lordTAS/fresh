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
from lxml         import etree
from ExistDBStore import ExistDBStore

update_query = '''
(: Creates a document if it does not exist. :)
declare function local:create-document($collection, $name, $xml)
{
  let $fullname := concat($collection, '/', $name)
  let $doc      := doc($fullname)
  return
  if ($doc) then
    $doc
  else
    let $status := xmldb:store($collection, $name, $xml)
    return doc($fullname)
};

let $coll    := '/db/%{collection}'
let $docname := '%{docname}'
let $country := <country>%{country}</country>
let $city    := <city>%{city}</city>
let $doc     := local:create-document($coll,
                                      $docname,
                                      <metadata hostname="%{hostname}"></metadata>)

return
<result>
    <document>
    {if ($doc) then <status>ok</status> else <status>failed</status>}
    </document>

    <country>
    {
      (: Insert or update the country tag. :)
      if (empty($doc//country)) then
        let $status := update insert $country into $doc/metadata
        return <status>inserted</status>
      else
        let $status := update replace $doc//country with $country
        return <status>updated</status>
    }
    </country>

    <city>
    {
      (: Insert or update the city tag. :)
      if (empty($doc//city)) then
        let $status := update insert $city into $doc/metadata
        return <status>inserted</status>
      else
        let $status := update replace $doc//city with $city
        return <status>updated</status>
    }
    </city>
</result>
'''

class ExistDBMetadataStore(ExistDBStore):
    def start(self, provider, conn, **kwargs):
        # Get the collection and document name.
        host       = conn.get_host()
        document   = kwargs.get('document')
        document   = self._replace_vars(host, document)
        collection = 'ips'  #FIXME: well this sucks
        if '/' in document:
            path, document = document.rsplit('/', 1)
            collection += '/' + path

        # Submit the metadata.
        host     = conn.get_host()
        address  = host.get_address()
        hostname = host.get_name()
        country  = host.get('country')
        city     = host.get('city')
        query    = self.db.query(update_query,
                                 collection = collection,
                                 docname    = document,
                                 hostname   = hostname,
                                 address    = address,
                                 country    = country,
                                 city       = city)

        # Check the response.
        for result in query:
            try:
                doc_result     = result.find('.//document/status').text
                country_result = result.find('.//country/status').text
                city_result    = result.find('.//city/status').text
            except AttributeError, e:
                err = str(e) + '\n' + etree.tostring(result)
                raise AttributeError(err)
            if doc_result != 'ok':
                err = 'error storing document %s: %s' % (document, doc_result)
                raise Exception(err)
            if country_result not in ('inserted', 'updated'):
                err = 'error updating country: %s' % country_result
                raise Exception(err)
            if city_result not in ('inserted', 'updated'):
                err = 'error updating country: %s' % country_result
                raise Exception(err)

        # Create a log entry.
        logger = host.get('__logger__')
        label  = host.get('__label__')
        logger.info('%s: Metadata %s updated.' % (label, document))
