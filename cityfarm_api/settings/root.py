from .base import *

NODE_TYPE = "ROOT"

INSTALLED_APPS = INSTALLED_APPS + ('root',)

MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
    'cityfarm_api.middleware.FarmRoutingMiddleware',
)

DATABASES = {
    'root': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}
