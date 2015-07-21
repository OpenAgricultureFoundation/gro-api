"""
This module defines a middleware class and a database router class that
together implement that logic allowing a root server to read from a different
database depending on the farm referenced by the current request.
"""
import threading

request_cfg = threading.local()

class FarmRoutingMiddleware:
    """
    Saves the name of the farm being accessed in a thread-local variable
    `request_cfg` during the request so that the database router can read form
    it.
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        if 'farm' in view_kwargs:
            request_cfg.farm = view_kwargs['farm']

    def process_response(self, request, response):
        if hasattr(request_cfg, 'farm'):
            del request_cfg.farm
        return response

class FarmDbRouter:
    """
    Uses the farm name saved in `request_cfg` to determine what database to
    read from.
    """
    def db_for_read(self, model, **hints):
        if hasattr(request_cfg, 'farm'):
            return request_cfg.farm
        return 'default'
