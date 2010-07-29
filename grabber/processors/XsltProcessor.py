import os, time
from StringIO import StringIO
from lxml     import etree

class XsltProcessor(object):
    def __init__(self, xsl_dir, add_timestamp = False):
        self.xsl_dir       = xsl_dir
        self.add_timestamp = add_timestamp

    def start(self, provider, conn, **kwargs):
        xslt_file = kwargs.get('xslt')
        xsd_file  = kwargs.get('xsd')
        infile    = kwargs.get('input')
        outfile   = kwargs.get('output')
        if not xslt_file.startswith('/'):
            xslt_file = os.path.join(self.xsl_dir, xslt_file)
        if xsd_file and not xsd_file.startswith('/'):
            xsd_file = os.path.join(self.xsl_dir, xsd_file)

        # Transform.
        xsl       = etree.parse(xslt_file)
        transform = etree.XSLT(xsl)
        path      = provider.store.get_path(conn, infile)
        input     = provider.store.get(conn, infile)
        doc       = etree.parse(StringIO(input), base_url = path)
        result    = transform(doc)

        # Add a timestamp field to the root node in the resulting XML.
        if self.add_timestamp:
            ts = time.asctime()
            etree.SubElement(result.getroot(), 'last-update').text = ts

        # Validate.
        if xsd_file:
            xsd    = etree.parse(xsd_file)
            schema = etree.XMLSchema(xsd)
            schema.assertValid(result)

        # Write.
        provider.store.store(conn, outfile, str(result))
