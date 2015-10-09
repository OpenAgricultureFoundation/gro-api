import os
from .base import *
from gro_state.gro_state.utils import ServerType

# Globals

DEBUG = True
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath( __file__))))

# Assign defaults for all system configuration parameters

PARENT_SERVER = None
SERVER_TYPE = ServerType.LEAF

### Installed apps

FRAMEWORK_APPS += (
    'debug_toolbar',
    'django_extensions',
)
DEBUG_TOOLBAR_PATCH_SETTINGS = False
INTERNAL_IPS = ['127.0.0.1']

INSTALLED_APPS = GRO_STATE_APPS + FRAMEWORK_APPS

### Request handling

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)
STATIC_ROOT = os.path.join(BASE_DIR, 'gro_state', 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'gro_state', 'media')

### Databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3')
    }
}

### Logging

LOGGING['loggers']['gro_state']['handlers'].append('console')
LOGGING['loggers']['django.security']['handlers'].append('console')
LOGGING['loggers']['django.request']['handlers'].append('console_request')

### Secret Key

SECRET_KEY = '@8i%f%y34i)t-g&9f&md3_y_v7a%rhh^@w$6$1%r8g=cb&^)29'
