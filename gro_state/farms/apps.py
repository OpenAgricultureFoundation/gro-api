from django.apps import AppConfig

class FarmsConfig(AppConfig):
    name = 'gro_state.farms'
    initial_fixtures = ['initial_groups']
