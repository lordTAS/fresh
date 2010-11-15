import sys, os
from setuptools import setup, find_packages

# Import the file that contains the version number.
fresh_dir = os.path.join(os.path.dirname(__file__), 'src', 'fresh')
sys.path.insert(0, fresh_dir)
from version import __version__

# Import the project description from the README.
readme = open('README').read()
start  = readme.index('\n\n')
end    = readme.index('\n\n=')
descr  = readme[start:end].strip()

# Run the setup.
setup(name             = 'Fresh',
      version          = __version__,
      description      = 'An automatic network inventory system',
      long_description = descr,
      author           = 'Samuel Abels',
      author_email     = 'knipknap@gmail.com',
      license          = 'GPLv2',
      package_dir      = {'fresh': os.path.join('src', 'fresh')},
      packages         = find_packages('src'),
      scripts          = [],
      install_requires = ['Exscript',
                          'Gelatin',
                          'lxml',
                          'pyexist',
                          'sqlalchemy'],
      keywords         = ' '.join(['fresh',
                                   'inventory',
                                   'exscript',
                                   'telnet',
                                   'ssh',
                                   'network',
                                   'networking',
                                   'automate',
                                   'automation',
                                   'library']),
      url              = 'https://github.com/knipknap/fresh/',
      classifiers      = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: System :: Networking',
        'Topic :: System :: Networking :: Monitoring'
      ])
