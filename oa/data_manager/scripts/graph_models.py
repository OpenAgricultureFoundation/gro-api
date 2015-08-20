import os
import sys
from itertools import chain
from django.conf import settings
from django.core.management import call_command
from .load_env import load_env

def graph_models():
    settings_module = 'oa.data_manager.data_manager.settings'
    os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
    load_env()
    app_labels = (
        path.split('.')[-1] for path in settings.OA_DATA_MANAGER_APPS
    )
    from django import setup
    setup()
    call_command('graph_models', *app_labels)

if __name__ == '__main__':
    graph_models()
