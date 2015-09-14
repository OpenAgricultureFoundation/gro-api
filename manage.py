#!/usr/bin/env python
import os
import sys
import shelve
from gro_api.scripts.load_env import load_env

if __name__ == "__main__":
    settings_module = 'gro_api.gro_api.settings'
    os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
    load_env()
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
