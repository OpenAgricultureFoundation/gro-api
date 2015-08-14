#!/usr/bin/env python
import os
import sys
import shelve

if __name__ == "__main__":
    if '--skip-env-loader' in sys.argv:
        sys.argv.remove('--skip-env-loader')
    else:
        env_vars_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'env_vars'
        )
        with shelve.open(env_vars_path) as env_vars:
            for key, val in env_vars.items():
                os.environ[key] = val
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
