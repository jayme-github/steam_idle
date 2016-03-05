#!/usr/bin/env python

from setuptools import setup

def parse_requirements(path):
    with open(path, 'r') as infile:
        return [l.strip() for l in infile.readlines()]

setup(
    name = 'steam_idle',
    version = '1.0',
    description = 'Idle Steam apps/games for card drops',
    long_description = open('README.rst', 'r').read(),
    platforms = ['any'],
    keywords = 'steam',
    author = 'Jayme',
    author_email = 'tuxnet@gmail.com',
    url = 'https://github.com/jayme-github/steam_idle',
    license = 'GNU Affero General Public License v3',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires = parse_requirements('requirements.txt'),
    packages = ['steam_idle'],
    package_dir = {'steam_idle': 'steam_idle'},
    package_data = {'steam_idle':
                    ['libs/steam_api64.dll',
                    'libs/libsteam_api.so',
                    'libs/steam_api.dll',
                    'libs/libsteam_api64.so',
                    'libs/libsteam_api.dylib']
    },
    scripts = ['steam_idle_cli.py'],
)
