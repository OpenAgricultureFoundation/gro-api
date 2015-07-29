"""
This module defines a middleware class and a database router class that
together implement that logic allowing a root server to read from a different
database depending on the farm referenced by the current request.
"""
from threading import currentThread
from django.conf import settings
from django.core.cache.backends.locmem import LocMemCache

_request_cache = {}

assert settings.SERVER_TYPE == settings.ROOT, \
    "The `cityfarm_api.middleware module should only be used in root servers"

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

class FarmDbRouter:
    """
    Uses the farm name saved in the request cache to determine what database to
    read from.
    """
    def db_for_read(self, model, **hints):
        return get_request_cache().get('farm')
