import os
import argparse
from django.conf import settings
from django.core.management import execute_from_command_line

def call_command():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', dest='debug', action='store_true')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if args.debug:
        settings_module = 'gro_state.core.settings.debug'
    else:
        settings_module = 'gro_state.core.settings.prod'
    os.environ['DJANGO_SETTINGS_MODULE'] = settings_module

    settings.INSTALLED_APPS

    from django import setup
    setup()

    execute_from_command_line([__file__] + args.args)

if __name__ == '__main__':
    call_command()
