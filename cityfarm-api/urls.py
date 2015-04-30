from django.conf.urls import include, url
from django.contrib import admin

from rest_framework.routers import DefaultRouter

from cityfarm-api import views

farm_router = DefaultRouter()
farm_router.register(r'farms', views.FarmViewset)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^/', include(farm_router.urls)),
]

if settings.NODE_TYPE == "ROOT":
    pass
elif settings.NODE_TYPE == "LEAF":
    pass
else:
    raise ImproperlyConfigured()
