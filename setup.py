#!/usr/bin/env python3

from setuptools import setup, find_packages

readme = open('README.rst', 'r')
README_TEXT = readme.read()
readme.close()

dev_reqs = [
    'django-debug-toolbar==1.3.2',
    'django-extensions==1.5.5',
]

setup(
    name = "gro_api",
    version = "0.1.0a0",
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'gro_api_configure = gro_api.scripts.configure:configure',
            'gro_api_load_env = gro_api.scripts.load_env:load_env',
            'gro_api_call_command = gro_api.scripts.call_command:call_command',
        ],
    },
    install_requires = [
        'awesome-slugify==1.6.5',
        'Django==1.8.4',
        'django-allauth==0.23.0',
        'django-cors-headers==1.1.0',
        'django-cron==0.4.3',
        'django-filter==0.11.0',
        'django-rest-auth==0.5.0',
        'django-rest-swagger==0.3.4',
        'django-solo==1.1.0',
        'djangorestframework==3.2.2',
        'PyYAML==3.11',
        'tortilla==0.4.1',
        'voluptuous==0.8.7',
    ],
    tests_require = dev_reqs,
    extras_require = {
        'dev': dev_reqs
    },
    test_suite = 'gro_api.scripts.runtests.runtests',
    # Metadata for PyPI
    long_description = README_TEXT,
    author = "Douglas Chambers",
    author_email = "leonchambers@mit.edu",
    license = "GPL",
)
