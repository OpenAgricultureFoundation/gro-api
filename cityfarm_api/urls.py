import sys

from django.conf import settings
from django.conf.urls import include, url

from rest_framework.routers import DefaultRouter

from farms import views as farm_views
from farms.models import Farm
from layout import views as layout_views

from cityfarm_api.errors import InvalidNodeType

def base_router():
    base_router = DefaultRouter()
    # Farm views
    base_router.register(r'farms', farm_views.FarmViewSet)
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
]

if settings.NODE_TYPE == "LEAF":
    farm = Farm.get_solo()
    urlpatterns.append(url(r'^', include(urls_for_farm(farm))))
elif settings.NODE_TYPE == "ROOT":
    # TODO: we don't need a root urlonf, but what does that mean for this block?
    pass
else:
    raise InvalidNodeType()
