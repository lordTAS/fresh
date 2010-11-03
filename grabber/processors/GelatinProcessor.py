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
import sys, os, glob, threading, traceback
from util         import str2filename
from Gelatin.util import compile, generate_string

class GelatinProcessor(object):
    def __init__(self, dirname, format):
        self.dirname      = dirname
        self.format       = format
        self.compile_lock = threading.Lock()
        self.converters   = {}
        self.conv_locks   = {}

    def _load_syntax(self, filename):
        with self.compile_lock:
            # Compiled files are cached.
            if self.converters.has_key(filename):
                return self.converters[filename]

            # Make sure that the file exists.
            full_filename             = os.path.join(self.dirname, filename)
            self.converters[filename] = compile(full_filename)
            self.conv_locks[filename] = threading.Lock()

            return self.converters[filename]

    def start(self, provider, conn, **kwargs):
        syntax    = kwargs.get('syntax')
        outfile   = kwargs.get('filename')
        converter = self._load_syntax(syntax)

        with self.conv_locks[syntax]:
            result = generate_string(converter, conn.response, self.format)

        provider.store.store(provider, conn, outfile, result)
