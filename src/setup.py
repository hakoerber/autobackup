from distutils.core import setup

setup(name='autobackup',
      version = '0.1-dev',
      description = '',
      long_description = open("README.md").read(),
      license = open("LICENSE").read(),
      author = 'Hannes Körber',
      author_email = 'hannes.koerber@gmail.com',
      url = 'http://github.com/whatevsz/autobackup/',
      packages=['apscheduler']
      )
