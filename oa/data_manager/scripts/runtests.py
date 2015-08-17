""" This file mainly exists to allow python `setup.py test` to work """
import os
import sys
from django import setup
from django.test.utils import get_runner
from django.conf import settings
from .load_env import load_env

def runtests():
    settings_module = 'oa.data_manager.data_manager.test_settings'
    os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
    load_env()
    setup()
    test_runner = get_runner(settings)
    failures = test_runner(verbosity=1, interactive=True).run_tests(())
    sys.exit(failures)

if __name__ == '__main__':
    runtests()
