from lxml import etree

class XsltProcessor(object):
    def __init__(self):
        pass

    def start(self, conn, **kwargs):
        host      = conn.get_host()
        hostname  = host.get('__real_hostname__')
        command   = host.get('__last_command__')
        xslt      = kwargs.get('xslt')
        filename  = kwargs.get('filename')

        # Transform.
        xsl_file  = os.path.join(self.dirname, 'xsl', 'generic.xsl')
        xsl       = etree.parse(xsl_file)
        transform = etree.XSLT(xsl)
        doc       = etree.parse(filename)
        result    = transform(doc)
        etree.SubElement(result.getroot(), 'last-update').text = time.asctime()

        # Validate.
        xsd_file = os.path.join(os.path.dirname(__file__), 'model.xsd')
        xsd      = etree.parse(xsd_file)
        schema   = etree.XMLSchema(xsd)
        schema.assertValid(result)

        # Write.
        xml     = str(result)
        dirname = os.path.dirname(filename)
        outfile = os.path.join(dirname, 'generic.xml')
        file    = open(outfile, 'w')
        file.write(xml)
        file.close()
