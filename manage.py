#!/usr/bin/env python
import os
import sys

import django
old_setup = django.setup
def new_setup():
    old_setup()
    from layout import monkey_patch_resolvers
django.setup = new_setup

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cityfarm_api.settings")

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
