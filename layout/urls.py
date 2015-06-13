from rest_framework.routers import DefaultRouter
from layout import views
from layout.schemata import all_schemata

router = DefaultRouter()
router.register(r'model3D', views.Model3DViewset)
router.register(r'trayLayout', views.TrayLayoutViewset)
router.register(r'plantSiteLayout', views.PlantSiteLayoutViewset)
router.register(r'layoutObject', views.LayoutObjectViewset)

urlpatterns = router.urls

def dynamic_urlpatterns(farm):
    router = DefaultRouter()
    if farm.layout:
        router.register(r'enclosure', views.EnclosureViewset)
        router.register(r'tray', views.TrayViewset)
        for entity in all_schemata[farm.layout]["entities"]:
            entity_name = entity["name"]
            entity_viewset = views.dynamic_viewsets[entity_name]
            router.register(entity_name, entity_viewset)
    return router.urls
