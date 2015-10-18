#!/usr/bin/env python3

from setuptools import setup, find_packages

readme = open('README.rst', 'r')
README_TEXT = readme.read()
readme.close()

dev_reqs = [
    'django-debug-toolbar==1.4',
    'django-extensions==1.5.7',
    'prospector==0.10.2'
]

setup(
    name = "gro_state",
    version = "0.2.0a0",
    packages = find_packages(),
    package_data = {
        'gro_state.layout.schemata': ['*.yaml'],
        'gro_state.farms.fixtures': ['*.json'],
        'gro_state.resources.fixtures': ['*.json'],
        'gro_state.sensors.fixtures': ['*.json'],
        'gro_state.actuators.fixtures': ['*.json'],
        'gro_state.control.fixtures': ['*.json'],
    },
    entry_points = {
        'console_scripts': [
            'gro_state = gro_state.core.scripts.call_command:call_command',
        ],
    },
    install_requires = [
        'awesome-slugify==1.6.5',
        'Django==1.8.5',
        'django-allauth==0.23.0',
        'django-cors-headers==1.1.0',
        'django-cron==0.4.3',
        'django-filter==0.11.0',
        'django-rest-auth==0.5.0',
        'django-rest-swagger==0.3.4',
        'django-solo==1.1.0',
        'django-uwsgi-cache==1.0.1',
        'djangorestframework==3.2.4',
        'mysqlclient==1.3.6',
        'PyYAML==3.11',
        'tortilla==0.4.1',
        'voluptuous==0.8.7',
    ],
    tests_require = dev_reqs,
    extras_require = {
        'dev': dev_reqs
    },
    test_suite = 'gro_state.core.scripts.runtests.runtests',
    # Metadata for PyPI
    long_description = README_TEXT,
    author = "Douglas Chambers",
    author_email = "leonchambers@mit.edu",
    license = "GPL",
)
