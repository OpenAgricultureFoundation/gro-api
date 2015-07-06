"""
This module defines a set of classes based on the view classes from
:mod:`rest_framework`. All viewsets in this project should inherit from the
viewsets in this module instead of using the ones in :mod:`rest_framework`
because they provide useful additional functionality
"""

from rest_framework import mixins as rest_mixins
from rest_framework import views as rest_views
from rest_framework import viewsets as rest_viewsets
from rest_framework import generics as rest_generics
from cityfarm_api.errors import FarmNotConfiguredError
from farms.models import Farm

class APIView(rest_views.APIView):
    """
    :class:`~rest_framework.views.APIView subclass that modifies :meth:`initial`
    to call :meth:`check`. This lets subclasses define additional checks to be
    performed on each request that don't fit cleanly into any of the standard
    categories: authentication, permissions, and throttles.
    """
    def initial(self, *args, **kwargs):
        """
        Calls meth:`check` after calling the :meth:`initial` method of the
        parent class
        """
        super().initial(*args, **kwargs)
        self.check()

    def check(self):
        """ There are no additional checks by default """
        pass

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

def farm_is_configured_check():
    """
    If the current farm has not been configured, don't allow the user to access
    this viewset.
    """
    if not Farm.get_solo().is_configured:
        raise FarmNotConfiguredError()

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
    def check(self):
        farm_is_configured_check()

class SingletonViewSet(rest_mixins.RetrieveModelMixin,
                       rest_mixins.UpdateModelMixin,
                       rest_mixins.ListModelMixin,
                       GenericViewSet):
    """
    Version of :class:`ModelViewSet` that works for
    :class:`solo.models.SingletonModel` instances. It doesn't allows for creates
    or destroys, and it makes sure the singleton has been created before
    rendering a list view.

    Subclasses of this class must define a class attribute :class:`model`, which
    is the name of the model about which this viewset displays information.
    """
    model = None

    def list(self, request, *args, **kwargs):
        # Create the singleton if it has not yet been created
        self.model.get_solo()
        return super().list(request, *args, **kwargs)

    def check(self):
        farm_is_configured_check()
