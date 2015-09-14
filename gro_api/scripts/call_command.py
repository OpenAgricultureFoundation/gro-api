#!/usr/bin/env python
import os
import sys
from django.core.management import call_command
from django.conf import settings
from .load_env import load_env

def runserver():
    settings_module = 'gro_api.gro_api.settings'
    os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
    load_env()
    # Our settings file monkey patches django.setup, so we have to force django
    # to load it before calling django.setup
    settings.INSTALLED_APPS
    from django import setup
    setup()
    call_command(*sys.argv[1:])

if __name__ == '__main__':
    runserver()
