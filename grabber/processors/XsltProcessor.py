import os, time
from lxml import etree

class XsltProcessor(object):
    def __init__(self, xsl_dir, output_dir):
        self.xsl_dir    = xsl_dir
        self.output_dir = output_dir

    def start(self, conn, **kwargs):
        host      = conn.get_host()
        path      = host.get('__path__')
        hostdir   = os.path.join(self.output_dir, path)
        xslt_file = kwargs.get('xslt')
        xsd_file  = kwargs.get('xsd')
        infile    = os.path.join(hostdir, kwargs.get('input'))
        outfile   = os.path.join(hostdir, kwargs.get('output'))
        if not xslt_file.startswith('/'):
            xslt_file = os.path.join(self.xsl_dir, xslt_file)
        if xsd_file and not xsd_file.startswith('/'):
            xsd_file = os.path.join(self.xsl_dir, xsd_file)

        # Transform.
        xsl       = etree.parse(xslt_file)
        transform = etree.XSLT(xsl)
        doc       = etree.parse(infile)
        result    = transform(doc)
        etree.SubElement(result.getroot(), 'last-update').text = time.asctime() #FIXME: should be configurable

        # Validate.
        if xsd_file:
            xsd    = etree.parse(xsd_file)
            schema = etree.XMLSchema(xsd)
            schema.assertValid(result)

        # Write.
        xml  = str(result)
        file = open(outfile, 'w')
        file.write(xml)
        file.close()
