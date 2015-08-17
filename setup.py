#!/usr/bin/env python3

from setuptools import setup, find_packages

dev_reqs = [
    'django-debug-toolbar>=1.3.2',
]

setup(
    name = "OA Data Manager",
    version = "0.1.0a0",
    namespace_packages = ['oa'],
    packages = ['oa.data_manager'],
    entry_points = {
        'console_scripts': [
            'oa_data_manager_configure = oa.data_manager.scripts.configure:configure',
            'oa_data_manager_runserver = oa.data_manager.scripts.runserver:runserver',
            'oa_data_manager_load_env = oa.data_manager.scripts.load_env:load_env',
        ],
    },
    install_requires = [
        'awesome-slugify>=1.6.5',
        'Django>=1.8.3',
        'django-allauth>=0.23.0',
        'django-cors-headers>=1.1.0',
        'django-cron>=0.4.3',
        'django-rest-auth>=0.4.0',
        'django-solo>=1.1.0',
        # '-e git+https://github.com/Tivix/django-cron.git@3e1eb09616c4830cc3623d71f40d61c7e7b9613b#egg=django_cron-master',
        # '-e git+https://github.com/lazybird/django-solo.git@c64e243a790092f47c3d0da806434c5bcb67c268#egg=django_solo-master',
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
