from django.apps import apps
from django.core.management import call_command
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        for app_config in apps.get_app_configs():
            if hasattr(app_config, 'initial_fixture'):
                call_command(
                    'loaddata', app_config.initial_fixture,
                    app=app_config.label
                )
        for app_config in apps.get_app_configs():
            if hasattr(app_config, 'setup_initial_data'):
                app_config.setup_initial_data()
