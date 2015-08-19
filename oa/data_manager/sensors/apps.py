from django.apps import AppConfig

class SensorsConfig(AppConfig):
    name = 'oa.data_manager.sensors'
    initial_fixture = 'initial_sensors'
