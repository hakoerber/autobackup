# -*- encoding: utf-8 -*-
from distutils.core import setup

VERSION = '0.1-dev'

# Look here for additional information about using the setup script:
# http://docs.python.org/2/distutils/index.html
# This is a list of all classifiers usable for the classifiers parameter in
# setup():
# https://pypi.python.org/pypi?%3Aaction=list_classifiers

setup(
      name='autobackup',
      version = VERSION,
      author = 'Hannes Körber',
      author_email = 'hannes.koerber@gmail.com',
      url = 'http://github.com/whatevsz/autobackup/',
      
      license = 'GNU GPL',
      platforms = ['Linux'],
      description = 'Backup deamon',
      long_description = open("README.md").read(),
     
#      package_dir = {'autobackup': 'packages'}, 
      packages = ['autobackup', 'tests'],
      scripts = ['scripts/autobackup.py'],
      data_files = [
          ('config', [
              'config/config.draft.xml', 
              'config/config.example.xml',
              'config/config.xsd']),
          ('', [
              'README.md']),
          ('documentation', [
              'documentation/TODO.txt',
              'documentation/CHANGELOG.txt',
              'documentation/INSTALL.txt',
              'documentation/STYLE.txt'])
          ],
      requires = ['apscheduler (>= 2.0.0)'],
      
      classifiers = [
          'Development Status :: 1 - Planning',
          'Environment :: No Input/Output (Daemon)',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Natural Language :: English',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2.7',
          'Topic :: System :: Archiving :: Backup'
          ]
      )
