#!/usr/bin/env python

from setuptools import setup
import os
import py2exe
import PyQt4
import requests.certs

print(PyQt4.__path__)

def parse_requirements(path):
    with open(path, 'r') as infile:
        return [l.strip() for l in infile.readlines()]

setup(
    name = 'steam_idle',
    version = '0.1',
    description = 'Idle your Steam libraty for cards',
    author = 'Jayme',
    author_email = 'tuxnet@gmail.com',
    url = 'https://github.com/jayme-github/steam_idle',
    install_requires = parse_requirements('requirements.txt'),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    packages = [
        'steam_idle',
        'steam_idle_qt'
    ],
    data_files = [
        ('libs', ['steam_idle/libs/steam_api64.dll',
                    'steam_idle/libs/libsteam_api.so',
                    'steam_idle/libs/steam_api.dll',
                    'steam_idle/libs/libsteam_api64.so',
                    'steam_idle/libs/libsteam_api.dylib']),
        ('', [requests.certs.where(),]),
        ('imageformats', [os.path.join(PyQt4.__path__[0], 'plugins', 'imageformats', 'qjpeg4.dll'),]),
    ],
    scripts = [
        'steam_idle_cli.py',
        'steam_idle_gui.py',
    ],
    windows = ['steam_idle_gui.py'],
    options = {
        'py2exe': {
            'includes': ['sip', 'PyQt4.QtCore', 'dbm.dumb'],
        },
    },
)
