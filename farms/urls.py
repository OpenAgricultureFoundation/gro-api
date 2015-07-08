from rest_framework.routers import DefaultRouter
from .models import Farm
from cityfarm_api.viewsets import model_viewsets

def register_static_patterns(router):
    router.register(r'farms', model_viewsets.get_for_model(Farm))

def register_dynamic_patterns(router, layout):
    pass
