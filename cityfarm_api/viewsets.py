from django.utils.functional import cached_property
from rest_framework import mixins as rest_mixins
from rest_framework import views as rest_views
from rest_framework import viewsets as rest_viewsets
from rest_framework import generics as rest_generics
import cityfarm_api.views as my_views
from cityfarm_api.errors import FarmNotConfiguredError
from farms.models import Farm

class ViewSet(rest_viewsets.ViewSetMixin, my_views.APIView):
    pass

class GenericViewSet(rest_viewsets.ViewSetMixin,
                     my_views.APIView,
                     rest_generics.GenericAPIView):
    pass

def farm_is_configured_check():
    if not Farm.get_solo().is_configured:
        raise FarmNotConfiguredError()

class ModelViewSet(rest_mixins.CreateModelMixin,
                   rest_mixins.RetrieveModelMixin,
                   rest_mixins.UpdateModelMixin,
                   rest_mixins.DestroyModelMixin,
                   rest_mixins.ListModelMixin,
                   GenericViewSet):
    def check(self):
        farm_is_configured_check()

class SingletonViewSet(rest_mixins.RetrieveModelMixin,
                       rest_mixins.UpdateModelMixin,
                       rest_mixins.ListModelMixin,
                       GenericViewSet):
    def list(self, request, *args, **kwargs):
        self.model.get_solo()
        return super().list(request, *args, **kwargs)

    def check(self):
        farm_is_configured_check()
