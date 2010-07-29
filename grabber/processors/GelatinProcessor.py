import sys, os, glob, threading, traceback
from util         import str2filename
from Gelatin.util import compile, generate_string_to_file

class GelatinProcessor(object):
    def __init__(self, dirname, output_dir):
        self.dirname      = dirname
        self.output_dir   = output_dir
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
        host      = conn.get_host()
        hostname  = host.get('__real_hostname__')
        path      = host.get('__path__')
        command   = host.get('__last_command__')
        syntax    = kwargs.get('syntax')
        host_dir  = os.path.join(self.output_dir, path)
        outfile   = kwargs.get('filename', str2filename(command, '.xml'))
        outfile   = os.path.join(host_dir, outfile)
        converter = self._load_syntax(syntax)

        with self.conv_locks[syntax]:
            generate_string_to_file(converter, conn.response, outfile, 'xml')
