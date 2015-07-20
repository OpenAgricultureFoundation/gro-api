"""
This module defines a set of classes based on the view classes from
:mod:`rest_framework`. All viewsets in this project should inherit from the
viewsets in this module instead of using the ones in :mod:`rest_framework`
because they provide useful additional functionality
"""

import logging
import importlib
from django.conf import settings
from rest_framework import mixins as rest_mixins
from rest_framework import views as rest_views
from rest_framework import viewsets as rest_viewsets
from rest_framework import generics as rest_generics
from .utils import ModelDict
from .errors import FarmNotConfiguredError
from .serializers import model_serializers
from .state import system_layout

logger = logging.getLogger(__name__)

class ViewSetRegistry(ModelDict):
    """
    A registry that keeps track of all of the viewsets that have been registered
    for this project.
    """
    def register(self, viewset):
        if hasattr(viewset, 'model'):
            if viewset.queryset is None:
                viewset.queryset = viewset.model.objects.all()
            if viewset.serializer_class is None:
                serializer = model_serializers.get_for_model(viewset.model)
                viewset.serializer_class = serializer
            self[viewset.model] = viewset

    def get_for_model(self, model):
        """
        Gets the viewset associated with the model `model`. If no viewset has
        been registered for the model, returns a :class:`ModelViewSet` subclass
        that can operate on the given model
        """
        if not model in self:
            class ViewSet(ModelViewSet): # pylint: disable=used-before-assignment
                queryset = model.objects.all()
                serializer_class = model_serializers.get_for_model(model)
            self[model] = ViewSet
        return self[model]

model_viewsets = ViewSetRegistry()

class APIViewMetaclass(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        model_viewsets.register(cls)

def farm_is_configured_check():
    """
    If the current farm has not been configured, don't allow the user to access
    this viewset.
    """
    if system_layout.current_value is None:
        raise FarmNotConfiguredError()

class APIView(rest_views.APIView, metaclass=APIViewMetaclass):
    """
    :class:`~rest_framework.views.APIView subclass that modifies :meth:`initial`
    to call :meth:`check`. This lets subclasses define additional checks to be
    performed on each request that don't fit cleanly into any of the standard
    categories: authentication, permissions, and throttles.
    """
    allow_access_with_unconfigured_farm = False

    def initial(self, *args, **kwargs):
        """
        Calls meth:`check` after calling the :meth:`initial` method of the
        parent class
        """
        super().initial(*args, **kwargs)
        self.check()

    def check(self):
        if not self.allow_access_with_unconfigured_farm:
            farm_is_configured_check()

class ViewSet(rest_viewsets.ViewSetMixin, APIView):
    """
    Version of :class:`rest_framework.viewsets.ViewSet` that inherits from
    :class:`cityfarm_api.views.APIView` instead of
    :class:`rest_framework.views.APIView`.
    """
    pass

class GenericViewSet(rest_viewsets.ViewSetMixin, APIView,
                     rest_generics.GenericAPIView):
    """
    Version of :class:`rest_framework.viewsets.GenericViewSet` that inherits
    from :class:`cityfarm_api.views.APIView` instead of
    :class:`rest_framework.views.APIView`.
    """
    pass

class ModelViewSet(rest_mixins.CreateModelMixin,
                   rest_mixins.RetrieveModelMixin,
                   rest_mixins.UpdateModelMixin,
                   rest_mixins.DestroyModelMixin,
                   rest_mixins.ListModelMixin,
                   GenericViewSet):
    """
    Version of :class:`rest_framework.viewsets.ModelViewSet` that inherits from
    :class:`cityfarm_api.views.APIView` instead of
    :class:`rest_framework.views.APIView`.
    """
    pass

class SingletonViewSetBase(APIViewMetaclass):
    def __init__(cls, name, bases, attrs):
        if 'model' in attrs:
            attrs['model'].get_solo()
        super().__init__(name, bases, attrs)

class SingletonViewSet(rest_mixins.RetrieveModelMixin,
                       rest_mixins.UpdateModelMixin,
                       rest_mixins.ListModelMixin,
                       GenericViewSet,
                       metaclass=SingletonViewSetBase):
    """
    Version of :class:`ModelViewSet` that works for
    :class:`solo.models.SingletonModel` instances. It doesn't allows for creates
    or destroys, and it makes sure the singleton has been created before
    rendering a list view.
    """
    pass


# Populate the viewset registry by making sure all viewset modules in this
# project have been imported
for app_name in settings.CITYFARM_API_APPS:
    try:
        importlib.import_module('.views', app_name)
    except ImportError as err:
        logger.debug(err)
