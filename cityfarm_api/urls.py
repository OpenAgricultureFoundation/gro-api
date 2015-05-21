import sys
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from cityfarm_api.errors import InvalidNodeType
from farms import views as farm_views
from farms.models import Farm
from layout import views as layout_views
from plants import views as plant_views


def base_router():
    base_router = DefaultRouter()
    base_router.register(r'farms', farm_views.FarmViewSet)
    base_router.register(r'model3D', layout_views.Model3DViewset)
    base_router.register(r'trayLayout', layout_views.TrayLayoutViewset)
    base_router.register(r'plantSiteLayout',
            layout_views.PlantSiteLayoutViewset)
    base_router.register(r'plantSite', plant_views.PlantSiteViewset)
    return base_router

def urls_for_farm(farm):
    router = base_router()
    # Layout views
    if farm.is_configured():
        for curr_viewset_name, curr_viewset in layout_views.all_viewsets[farm.layout].items():
            router.register(curr_viewset_name, curr_viewset)
    return router.urls

urlpatterns = [
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.NODE_TYPE == "LEAF":
    farm = Farm.get_solo()
    urlpatterns.append(url(r'^', include(urls_for_farm(farm))))
elif settings.NODE_TYPE == "ROOT":
    # TODO: we don't need a root urlonf, but what does that mean for this block?
    pass
else:
    raise InvalidNodeType()
