import configparser
from django.core.exceptions import ImproperlyConfigured
from .base import *

# Globals

DEBUG = False

# Read the system configuration file

SYSTEM_CONF_FILENAME = '/etc/gro.conf'

config = configparser.ConfigParser()
config.read(SYSTEM_CONF_FILENAME)
try:
    SECRET_KEY = config.get('state', 'SECRET_KEY')
except configparser.NoSectionError:
    raise ImproperlyConfigured(
        'Configuration file did not contain a value for SECRET_KEY'
    )

### Installed apps

INSTALLED_APPS = GRO_STATE_APPS + FRAMEWORK_APPS

### Request handling

STATIC_ROOT = '/var/www/gro/static'
MEDIA_ROOT = '/var/www/gro/media'

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

### Databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': SYSTEM_CONF_FILENAME
        }
    }
}

### Logging

error_filename = '/var/log/gro/state/error.log'
LOGGING['handlers']['error_file'] = {
    'level': 'INFO',
    'class': 'logging.FileHandler',
    'formatter': 'verbose',
    'filename': error_filename
}
LOGGING['handlers']['error_file_request'] = {
    'level': 'INFO',
    'class': 'logging.FileHandler',
    'formatter': 'verbose_request',
    'filename': error_filename
}
LOGGING['loggers']['gro_state']['handlers'].append('error_file')
LOGGING['loggers']['django.security']['handlers'].append('error_file')
LOGGING['loggers']['django.request']['handlers'].append('error_file_request')
