#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = "OAPI",
    version = "0.1.0a0",
    packages = find_packages(),
    scripts = ['generate_openag_env.sh'],
    install_requires = [
        'awesome-slugify==1.6.5',
        'Django==1.8.3',
        'django-cors-headers==1.1.0',
        # '-e git+https://github.com/Tivix/django-cron.git@3e1eb09616c4830cc3623d71f40d61c7e7b9613b#egg=django_cron-master',
        # '-e git+https://github.com/lazybird/django-solo.git@c64e243a790092f47c3d0da806434c5bcb67c268#egg=django_solo-master',
        'djangorestframework==3.1.3',
        'PyYAML==3.11',
        'tortilla==0.4.1',
        'voluptuous==0.8.7',
    ],
    # Testing
    # tests_require = [
    # ],
    test_suite = 'cityfarm_api.runtests.runtests',
    # Metadata for PyPI
    author = "Douglas Chambers",
    author_email = "leonchambers@mit.edu",
    license = "GPL",
)
