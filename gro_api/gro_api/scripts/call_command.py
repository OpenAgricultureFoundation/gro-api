#!/usr/bin/env python
import os
import sys
from django.conf import settings
from django.core.management import call_command as call_django_command

def call_command():
    settings_module = 'gro_api.gro_api.settings'
    os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
    # Our settings file monkey patches django.setup, so we have to force django
    # to load it before calling django.setup
    settings.INSTALLED_APPS
    from django import setup
    setup()
    call_django_command(*sys.argv[1:])

if __name__ == '__main__':
    call_command()
