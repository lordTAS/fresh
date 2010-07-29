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

        provider.store.store(conn, outfile, result)
