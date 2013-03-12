# -*- encoding: utf-8 -*-
from distutils.core import setup

VERSION = '0.1-dev'

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
     
      package_dir = {'autobackup': 'src'}, 
      packages = ['autobackup', 'tests'],
      scripts = ['scripts/autobackup.py'],
      data_files = [
          ('cfg', [
              'cfg/config.draft.xml', 
              'cfg/config.example.xml',
              'cfg/config.xsd']),
          ('', [
              'README.md']),
          ('doc', [
              'doc/TODO.txt',
              'doc/CHANGELOG.txt',
              'doc/INSTALL.txt',
              'doc/STYLE.txt'])
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
