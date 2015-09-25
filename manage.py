#!/usr/bin/env python3
import os
import sys

if __name__ == "__main__":
    settings_module = 'gro_api.gro_api.settings'
    os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
