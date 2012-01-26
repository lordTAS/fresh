import sys, os
from setuptools import setup, find_packages
pkg = 'fresh'

# Import the file that contains the version number.
fresh_dir    = os.path.join(os.path.dirname(__file__), 'src', pkg)
provider_dir = os.path.join('grabber', 'providers')
sys.path.insert(0, fresh_dir)
from version import __version__

# Import the project description from the README.
readme = open('README').read()
start  = readme.index('\n\n')
end    = readme.index('\n\n=')
descr  = readme[start:end].strip()

# Run the setup.
setup(name             = pkg,
      version          = __version__,
      description      = 'An automatic network inventory system',
      long_description = descr,
      author           = 'Samuel Abels',
      author_email     = 'knipknap@gmail.com',
      license          = 'GPLv2',
      package_dir      = {pkg: os.path.join('src', pkg)},
      package_data     = {pkg: [
                            os.path.join('grabber', 'xsl', '*.xsl'),
                            os.path.join('grabber', 'xsl', 'model.xsd'),
                            os.path.join(provider_dir, 'ios', 'gel', '*.gel'),
                            os.path.join(provider_dir, 'ios', 'xsl', '*.xsl'),
                            os.path.join(provider_dir, 'ios_xr', 'gel', '*.gel'),
                            os.path.join(provider_dir, 'ios_xr', 'xsl', '*.xsl'),
                            os.path.join(provider_dir, 'junos', 'gel', '*.gel'),
                            os.path.join(provider_dir, 'junos', 'xsl', '*.xsl'),
                         ]},
      packages         = find_packages('src'),
      scripts          = [],
      install_requires = ['Exscript',
                          'Gelatin',
                          'lxml',
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
