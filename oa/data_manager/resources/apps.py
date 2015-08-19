from django.apps import AppConfig

class ResourcesConfig(AppConfig):
    name = 'oa.data_manager.resources'
    initial_fixture = 'initial_resources'
