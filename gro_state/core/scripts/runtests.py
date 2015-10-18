import os
import sys
from django.conf import settings
from django.test.utils import get_runner

def runtests():
    settings_module = 'gro_state.core.settings.debug'
    os.environ['DJANGO_SETTINGS_MODULE'] = settings_module

    # Force the settings file to be loaded before django.setup is called
    settings.INSTALLED_APPS
    from django import setup
    setup()

    test_runner = get_runner(settings)
    failures = test_runner(verbosity=1, interactive=True).run_tests(())
    sys.exit(failures)

if __name__ == '__main__':
    runtests()
