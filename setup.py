#!/usr/bin/env python

# setup.py
# Install script for pysbserver
# Copyright (c) 2012 Morgan Borman
# E-mail: morgan.borman@gmail.com

# This software is licensed under the terms of the Zlib license.
# http://en.wikipedia.org/wiki/Zlib_License

from distutils.core import setup
from pysbserver import __version__ as VERSION

NAME = "pysbserver"

PACKAGES = ['pysbserver']
				
PACKAGE_DATA = {'': ['sauerbraten_server']}

DESCRIPTION = 'A python implementation of the sauerbraten server'

URL = 'https://github.com/MorganBorman/pysbserver'

DOWNLOAD_URL = "https://github.com/MorganBorman/pysbserver/downloads"

AUTHOR = 'Morgan Borman'

AUTHOR_EMAIL = 'morgan.borman@gmail.com'

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: zlib/libpng License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Operating System :: OS Independent',
    'Topic :: Internet',
    'Topic :: Games/Entertainment :: First Person Shooters',
    'Natural Language :: English'
]

setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url=URL,
      download_url=DOWNLOAD_URL,
      packages=PACKAGES,
      package_data=PACKAGE_DATA,
      classifiers=CLASSIFIERS
     )