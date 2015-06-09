import sys
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from cityfarm_api.errors import InvalidNodeType
from farms import views as farm_views
from farms.models import Farm
from layout import views as layout_views
from layout.schemata import all_schemata
from plants import views as plant_views


def base_router():
    router = DefaultRouter()
    # Farm Viewsets
    router.register(r'farms', farm_views.FarmViewset)
    # Layout Viewsets
    router.register(r'model3D', layout_views.Model3DViewset)
    router.register(r'trayLayout', layout_views.TrayLayoutViewset)
    router.register(r'plantSiteLayout',
            layout_views.PlantSiteLayoutViewset)
    router.register(r'layoutObject', layout_views.LayoutObjectViewset)
    # Plant Viewsets
    router.register(r'plantSite', plant_views.PlantSiteViewset)
    router.register(r'plantType', plant_views.PlantTypeViewset)
    router.register(r'plant', plant_views.PlantViewset)
    return router

def urls_for_farm(farm):
    router = base_router()
    if farm.layout:
        router.register(r'enclosure', layout_views.EnclosureViewset)
        router.register(r'tray', layout_views.TrayViewset)
        # Layout views
        for entity in all_schemata[farm.layout]["entities"]:
            entity_name = entity["name"]
            entity_viewset = layout_views.dynamic_viewsets[entity_name]
            router.register(entity_name, entity_viewset)
    return router.urls

def base_urlconf():
    return [
        url(r'^auth/', include('rest_framework.urls',
            namespace='rest_framework')),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

def urlconf_for_farm(farm):
    urlconf = base_urlconf()
    urlconf.append(url(r'^', include(urls_for_farm(farm))))
    return urlconf


if settings.NODE_TYPE == "LEAF":
    urlpatterns = urlconf_for_farm(Farm.get_solo())
elif settings.NODE_TYPE == "ROOT":
    print("Running as root")
    # TODO: we don't need a root urlonf, but what does that mean for this block?
    pass
else:
    raise InvalidNodeType()
