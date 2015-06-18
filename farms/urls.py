from rest_framework.routers import DefaultRouter
from farms import views

def register_static_patterns(router):
    router.register(r'farms', views.FarmViewset)

def register_dynamic_patterns(router, layout):
    pass
