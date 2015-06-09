import os
from .base import *

NODE_TYPE = "LEAF"

INSTALLED_APPS = INSTALLED_APPS + ('control',)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
