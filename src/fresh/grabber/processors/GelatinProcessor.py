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
import os
import threading
from collections  import defaultdict
from util         import str2filename
from Gelatin.util import compile, generate_string
from Processor    import Processor

class GelatinProcessor(Processor):
    def __init__(self, dirname, format):
        self.dirname      = dirname
        self.format       = format
        self.compile_lock = threading.Lock()
        self.converters   = defaultdict(list)

    def _acquire_converter(self, syntax_filename):
        with self.compile_lock:
            try:
                converter = self.converters[syntax_filename].pop()
            except IndexError:
                filename  = os.path.join(self.dirname, syntax_filename)
                converter = compile(filename)
            return converter

    def _release_converter(self, syntax_filename, converter):
        with self.compile_lock:
            self.converters[syntax_filename].append(converter)

    def start(self, provider, host, conn, **kwargs):
        syntax    = kwargs.get('syntax')
        outfile   = kwargs.get('filename')
        converter = self._acquire_converter(syntax)

        try:
            result = generate_string(converter, conn.response, self.format)
        finally:
            self._release_converter(syntax, converter)

        provider.store.store(provider, host, outfile, result)
