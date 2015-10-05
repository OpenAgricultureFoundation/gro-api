import shelve
from pkg_resources import resource_filename
from django.core.management.base import BaseCommand, CommandError

class ConfigureServer(BaseCommand):
    can_import_settings = False

    def add_arguments(self, parser):
        parser.add_argument(
            '--dev', '-d', dest='development', action='store_true',
            default=False, help='Run in development mode'
        )
        parser.add_argument(
            '--root', '-r', dest='root', action='store_true', default=False,
            help='Run a root server'
        )

    def handle(self, *args, **options):
        import pdb; pdb.set_trace()
        # Can we use __package__ to get the package name?
        env_vars_path = resource_filename('gro_api', 'env_vars')
        env_vars = shelve.open(env_vars_path)
        try:
            env_vars['GRO_API_ROOT'] = base_path
            if args.development:
                env_vars['GRO_API_SERVER_MODE'] = 'development'
                env_vars['UWSGI_MASTER_FIFO'] = oa.path.join()
        finally:
            env_vars.close()
