from django.apps import AppConfig

class ControlConfig(AppConfig):
    name = 'oa.data_manager.control'
    initial_fixture = 'initial_controls'
