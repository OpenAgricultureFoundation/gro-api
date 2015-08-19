#!/usr/bin/env python3

from setuptools import setup, find_packages

dev_reqs = [
    'django-debug-toolbar>=1.3.2',
]

setup(
    name = "OA Data Manager",
    version = "0.1.0a0",
    namespace_packages = ['oa'],
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'oa_data_manager_configure = oa.data_manager.scripts.configure:configure',
            'oa_data_manager_load_env = oa.data_manager.scripts.load_env:load_env',
        ],
    },
    install_requires = [
        'awesome-slugify>=1.6.5',
        'Django>=1.8.3',
        'django-allauth>=0.23.0',
        'django-cors-headers>=1.1.0',
        'django-cron>=0.4.3',
        'django-filter>=0.11.0',
        'django-rest-auth>=0.4.0',
        'django-solo>=1.1.0',
        'djangorestframework>=3.1.3',
        'PyYAML>=3.11',
        'tortilla>=0.4.1',
        'voluptuous>=0.8.7',
    ],
    tests_require = dev_reqs,
    extras_require = {
        'dev': dev_reqs
    },
    test_suite = 'oa.data_manager.scripts.runtests.runtests',
    # Metadata for PyPI
    author = "Douglas Chambers",
    author_email = "leonchambers@mit.edu",
    license = "GPL",
)
