from rest_framework.routers import DefaultRouter
from plants import views

def register_static_patterns(router):
    router.register(r'plantSite', views.PlantSiteViewset)
    router.register(r'plantType', views.PlantTypeViewset)
    router.register(r'plant', views.PlantViewset)

def register_dynamic_patterns(router, layout):
    pass
