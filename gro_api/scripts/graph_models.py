import os
import sys
from itertools import chain
from django.conf import settings
from django.core.management import call_command
from .load_env import load_env

def graph_models():
    settings_module = 'gro_api.gro_api.settings'
    os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
    load_env()
    from django import setup
    setup()
    call_command('graph_models', *sys.argv[1:])

if __name__ == '__main__':
    graph_models()
