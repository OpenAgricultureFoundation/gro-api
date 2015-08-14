""" This file mainly exists to allow python `setup.py test` to work """
import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'cityfarm_api.test_settings'

from django import setup
from django.test.utils import get_runner
from django.conf import settings

def runtests():
    setup()
    test_runner = get_runner(settings)
    failures = test_runner(verbosity=1, interactive=True).run_tests(())
    sys.exit(failures)

if __name__ == '__main__':
    runtests()
