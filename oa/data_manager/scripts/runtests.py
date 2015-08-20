""" This file mainly exists to allow python `setup.py test` to work """
import os
import sys
from django.conf import settings
from django.test.utils import get_runner
from .load_env import load_env

def runtests():
    settings_module = 'oa.data_manager.data_manager.test_settings'
    os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
    load_env()
    # Our settings file monkey patches django.setup, so we have to force django
    # to load it before calling django.setup
    settings.INSTALLED_APPS
    from django import setup
    setup()
    test_runner = get_runner(settings)
    failures = test_runner(verbosity=1, interactive=True).run_tests(())
    sys.exit(failures)

if __name__ == '__main__':
    runtests()
