import threading
from django.http import Http404

request_cfg = threading.local()

class FarmRoutingMiddleware:
    def process_view(self, request, view_func, view_args, view_kwargs):
        if 'farm' in kwargs:
            request_cfg.db = kwargs['farm']
    def process_response(self, request, response):
        if hasattr(request_cfg, 'farm'):
            del request_cfg.farm
        return response

class FarmDbRouter:
    def db_for_read(self, model, **hints):
        if hasattr(request_cfg, 'farm'):
            return request_cfg.farm
        return 'default'
