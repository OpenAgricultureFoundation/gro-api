import configparser
from django.core.exceptions import ImproperlyConfigured
from .base import *
from gro_state.gro_state.utils import ServerType

# Globals

DEBUG = False

# Read the system configuration file

SYSTEM_CONF_FILENAME = '/etc/gro.conf'

config = configparser.ConfigParser()
config.read(SYSTEM_CONF_FILENAME)
PARENT_SERVER = config.get(
    'gro', 'PARENT_SERVER', fallback='openag.mit.edu'
)
server_type = config.get(
    'gro', 'SERVER_TYPE', fallback=ServerType.LEAF.name
)
try:
    SERVER_TYPE = next(
        val for name, val in ServerType.__members__.items() if name ==
        server_type
    )
except StopIteration:
    raise ImproperlyConfigured(
        'Configuration file contained an invalid value "{}" for '
        'SERVER_TYPE'.format(server_type)
    )
SECRET_KEY = config.get('state', 'SECRET_KEY')

### Installed apps

INSTALLED_APPS = GRO_STATE_APPS + FRAMEWORK_APPS

### Request handling

STATIC_ROOT = '/var/www/gro/static'
MEDIA_ROOT = '/var/www/gro/media'

if SERVER_TYPE == ServerType.ROOT:
    DATABASE_ROUTERS = ['gro_state.middleware.FarmDbRouter']

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

### Databases

if SERVER_TYPE == ServerType.LEAF:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'OPTIONS': {
                'read_default_file': SYSTEM_CONF_FILENAME
            }
        }
    }
else:
    # TODO: Setup a database for every registered farm
    raise NotImplementedError()

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
