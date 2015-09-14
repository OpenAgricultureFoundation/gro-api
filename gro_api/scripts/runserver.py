import os
from django.conf import settings
from .load_env import load_env

def runserver():
    settings_module = 'gro_api.gro_api.settings'
    os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
    load_env()
    settings.INSTALLED_APPS
    from django import setup
    setup()
    call_command('runserver', *sys.argv[1:])

if __name__ == '__main__':
    runserver()
