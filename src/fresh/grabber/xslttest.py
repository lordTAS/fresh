#!/usr/bin/env python
import os
import sys
from optparse import OptionParser
from lxml import etree
from util import apply_xslt

parser = OptionParser(usage = '%prog xslt_file xml_file')
options, args = parser.parse_args(sys.argv)
args.pop(0)

try:
    xslt_file = args.pop(0)
except IndexError:
    parser.error('please the name of the XSLT file')

try:
    xml_file = args.pop(0)
except IndexError:
    parser.error('please enter the name of the XML file')

path = os.path.basename(xml_file)
doc = etree.parse(xml_file, base_url = path)
xsl = etree.parse(xslt_file)

print apply_xslt(xsl, doc)
