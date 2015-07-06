from layout import models
from layout import views

def register_static_patterns(router):
    router.register(r'model3D', views.Model3DViewSet)
    # router.register(r'trayLayout', views.TrayLayoutViewSet)
    # router.register(r'plantSiteLayout', views.PlantSiteLayoutViewSet)

def register_dynamic_patterns(router, layout):
    router.register(r'enclosure', views.EnclosureViewSet)
    router.register(r'tray', views.TrayViewSet)
    for entity_slug, entity_model in models.dynamic_models.items():
        entity_viewset = views.dynamic_viewsets[entity_slug]
        router.register(entity_slug.lower(), entity_viewset)
