from .base import *

NODE_TYPE = "ROOT"

MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
    'cityfarm-api.middleware.FarmRoutingMiddleware',
)
