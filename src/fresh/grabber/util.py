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
import re
import os
from lxml import etree

filename_strip_re = re.compile(r'[^a-z0-9_\-\.]', re.I)

def str2filename(string, suffix = '.txt'):
    filename = filename_strip_re.sub('', string.replace(' ', '_'))
    if not '.' in filename:
        filename += suffix
    return filename

python_ns = etree.FunctionNamespace('localhost')
python_ns.prefix = 'py'
python_ns['file-exists'] = lambda c, x: os.path.isfile(x)

def apply_xslt(xslt, doc):
    transform = etree.XSLT(xslt)
    return transform(doc)
