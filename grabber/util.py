import re

filename_strip_re = re.compile(r'[^a-z0-9_\-\.]', re.I)

def str2filename(string, suffix = '.txt'):
    filename = filename_strip_re.sub('', string.replace(' ', '_'))
    if not '.' in filename:
        filename += suffix
    return filename
