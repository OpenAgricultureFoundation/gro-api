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
from .utils import system_layout

_request_cache = {}

def get_request_cache():
    """ Returns the cache for the current thread """
    if not currentThread() in _request_cache:
        _request_cache[currentThread()] = RequestCache()
    return _request_cache[currentThread()]


class RequestCache(LocMemCache):
    """ A local memory cache specific to the current thread """
    def __init__(self):
        name = 'locmemcache@%i' % hash(currentThread())
        params = dict()
        super().__init__(name, params)


class RequestCacheMiddleware:
    """
    Clears the current per-request thread once a response has been generated
    """
    def process_response(self, request, response):
        if currentThread() in _request_cache:
            _request_cache[currentThread()].clear()


class FarmRoutingMiddleware:
    """
    Saves the name of the farm being accessed in the per-request cache during
    the request so that the database router can read form it.
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        if 'farm' in view_kwargs:
            get_request_cache().set('farm', view_kwargs['farm'])


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
        if not getattr(view_func.cls, 'allow_on_unconfigured_farm', False):
            return self.view(request)


class FarmDbRouter:
    """
    Uses the farm name saved in the request cache to determine what database to
    read from.
    """
    def db_for_read(self, model, **hints):
        return get_request_cache().get('farm')

    def allow_migrate(db, app_label, model_name=None, **hints):
        if settings.SERVER_TYPE == settings.ROOT:
            # TODO: Rework this. The will be some tables in the root server
            # that will need to be migrated at some point.
            return False
