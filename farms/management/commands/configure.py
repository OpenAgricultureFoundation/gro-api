from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from farms.models import Farm

def get_string_argument(key, options):
    return options[key] or input("What is the %s of your farm: " % key)

class Command(BaseCommand):
    help = 'Configures the farm-specific settings of the server'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.requires_system_checks = False
    def add_arguments(self, parser):
        parser.add_argument('--name', action='store', nargs='?')
        parser.add_argument('--subdomain', action='store', nargs='?')
        parser.add_argument('--layout', action='store', nargs='?')
        parser.add_argument('--ip', action='store', nargs='?')
    def handle(self, *args, **options):
        if settings.NODE_TYPE == "ROOT":
            raise CommandError("There is no need to configure a root server")
        elif settings.NODE_TYPE != "LEAF":
            raise ImproperlyConfigured('NODE_TYPE must be "LEAF" or "ROOT"')
        name = get_string_argument('name', options)
        subdomain = get_string_argument('subdomain', options)
        # TODO: define the set of choices for layout
        layout = get_string_argument('layout', options)
        ip = get_string_argument('ip', options)
        # TODO: better error checking on this create
        Farm.objects.get_or_create(name=name, subdomain=subdomain, layout=layout, ip=ip)
