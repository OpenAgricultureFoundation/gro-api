from django.apps import apps
from django.core.management import call_command
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        self.apps_loaded = {}
        for app_config in apps.get_app_configs():
            self.load_app_data(app_config)

    def load_app_data(self, app_config):
        if self.apps_loaded.get(app_config.label, False):
            return
        if hasattr(app_config, 'data_dependencies'):
            for dependency in app_config.data_dependencies:
                self.load_app_data(apps.get_app_config(dependency))
        if hasattr(app_config, 'initial_fixture'):
            call_command(
                'loaddata', app_config.initial_fixture, app=app_config.label
            )
        if hasattr(app_config, 'setup_initial_data'):
            app_config.setup_initial_data()
        self.apps_loaded[app_config.label] = True
