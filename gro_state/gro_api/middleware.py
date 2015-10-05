"""
This module defines a middleware class and a database router class that
together implement that logic allowing a root server to read from a different
database depending on the farm referenced by the current request.
"""
from threading import currentThread
from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.core.cache.backends.locmem import LocMemCache
from rest_framework.views import APIView
from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny
from .utils.layout import system_layout
from ..farms.models import Farm

class FarmNotConfiguredError(APIException):
    """
    This exception should be thrown when a user attempts to input data for a
    model in farm that has not yet been configured.
    """
    status_code = 403
    default_detail = (
        "Please configure your farm before attempting to save data in this API"
    )

class FarmIsConfiguredCheckMiddleware:
    """
    Hides all views except for the farm view if the current farm is not
    configured
    """
    def __init__(self):
        if system_layout.current_value is not None:
            raise MiddlewareNotUsed()
        class FarmNotConfiguredView(APIView):
            permission_classes = (AllowAny, )
            def get(self, request):
                raise FarmNotConfiguredError()
            post = get
            put = get
            patch = get
            delete = get
        self.view = FarmNotConfiguredView.as_view()

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not Farm.get_solo().slug:
            return self.view(request)

class FarmDbRouter:
    """
    Uses the farm name saved in the request cache to determine what database to
    read from.
    """
    def db_for_read(self, model, **hints):
        return os.environ['CURRENT_FARM']

    def allow_migrate(db, app_label, model_name=None, **hints):
        if settings.SERVER_TYPE == ServerType.ROOT:
            # TODO: Rework this. The will be some tables in the root server
            # that will need to be migrated at some point.
            return False
