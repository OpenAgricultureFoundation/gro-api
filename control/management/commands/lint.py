import os
from pylint import epylint as lint
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Performs linting on the codebase using pylint'

    def add_arguments(self, parser):
        parser.add_argument('modules', nargs='*')
        parser.add_argument(
            '--rcfile', dest='rcfile',
            default=os.path.join(settings.BASE_DIR, '.pylintrc')
        )

    def handle(self, *args, **options):
        rcfile = options.get('rcfile')
        default_modules = settings.CITYFARM_API_APPS + ('cityfarm_api',)
        modules = ' '.join(options.get('modules') or default_modules)
        lint.py_run('--rcfile={} {}'.format(rcfile, modules), script='pylint')
