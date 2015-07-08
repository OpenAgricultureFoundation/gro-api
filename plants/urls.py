from rest_framework.routers import DefaultRouter
from cityfarm_api.viewsets import model_viewsets
from .models import PlantSite, PlantType, Plant

def register_static_patterns(router):
    router.register(r'plantSite', model_viewsets.get_for_model(PlantSite))
    router.register(r'plantType', model_viewsets.get_for_model(PlantType))
    router.register(r'plant', model_viewsets.get_for_model(Plant))

def register_dynamic_patterns(router, layout):
    pass
