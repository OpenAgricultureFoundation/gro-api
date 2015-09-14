"""
Django settings for the gro-api project
"""
import os
import sys
import django
import string
from django.core.exceptions import ImproperlyConfigured

old_setup = django.setup
if not getattr(old_setup, 'is_patched', False):
    def new_setup():
        from .patch_resolvers import patch_resolvers
        from .disable_patch import disable_patch
        patch_resolvers()
        disable_patch()
        old_setup()
    new_setup.is_patched = True
    django.setup = new_setup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework.authentication.TokenAuthentication',),
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS': 'gro_api.gro_api.pagination.Pagination',
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly', ),
    'EXCEPTION_HANDLER': 'gro_api.gro_api.views.exception_handler',
    'PAGE_SIZE': 100,
}

# Local Configuration

LEAF = "leaf"
ROOT = "root"

DEVELOPMENT = "development"
PRODUCTION = "production"

try:
    SERVER_TYPE = os.environ['GRO_API_SERVER_TYPE']
    SERVER_MODE = os.environ['GRO_API_SERVER_MODE']
except KeyError:
    raise ImproperlyConfigured(
        'Run gro_api_configure before attempting to run anything.'
    )

if SERVER_TYPE not in [LEAF, ROOT]:
    raise ValueError('Invalid server type read from environment')

if SERVER_MODE not in [DEVELOPMENT, PRODUCTION]:
    raise ValueError('Invalid server mode read from environment')

if SERVER_MODE == DEVELOPMENT:
    DEBUG = True
else:
    DEBUG = False

# Installed Apps

GRO_API_APPS = (
    'gro_api.farms',
    'gro_api.layout',
    'gro_api.plants',
    'gro_api.resources',
    'gro_api.sensors',
    'gro_api.actuators',
    'gro_api.recipes',
)

if SERVER_TYPE == LEAF:
    GRO_API_APPS = GRO_API_APPS + ('gro_api.control',)

FRAMEWORK_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_cron',
    'corsheaders',
    'rest_framework',
    # Authentication apps
    'rest_framework.authtoken',
    'rest_auth',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_auth.registration',
    'rest_framework_swagger',
)

if SERVER_MODE == DEVELOPMENT:
    FRAMEWORK_APPS += (
        'debug_toolbar',
        'django_extensions',
    )
    DEBUG_TOOLBAR_PATCH_SETTINGS = False
    INTERNAL_IPS = ['127.0.0.1']

INSTALLED_APPS = GRO_API_APPS + FRAMEWORK_APPS

# Request Handling

WSGI_APPLICATION = 'gro_api.gro_api.wsgi.application'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

if SERVER_TYPE == ROOT:
    MIDDLEWARE_CLASSES += (
        'gro_api.gro_api.middleware.RequestCacheMiddleware',
        'gro_api.gro_api.middleware.FarmRoutingMiddleware',
    )
else:
    MIDDLEWARE_CLASSES += (
        'gro_api.gro_api.middleware.FarmIsConfiguredCheckMiddleware',
    )

if SERVER_MODE == DEVELOPMENT:
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = (
    'This is a fake module; if django tries to load this, you broke something'
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

if SERVER_TYPE == ROOT:
    DATABASE_ROUTERS = ['gro_api.middleware.FarmDbRouter']

STATIC_URL = '/static/'
if SERVER_MODE == DEVELOPMENT:
    STATIC_ROOT = os.path.join(BASE_DIR, 'gro_api', 'static')
else:
    STATIC_ROOT = '/var/www/gro_api/static'

MEDIA_URL = '/media/'
if SERVER_MODE == DEVELOPMENT:
    MEDIA_ROOT = os.path.join(BASE_DIR, 'gro_api', 'media')
else:
    MEDIA_ROOT = '/var/www/gro_api/media'

if SERVER_TYPE == LEAF:
    # TODO: We could dynamically generate this from the current ip address?
    # There is no guarantee about what host leaf servers will run behind
    ALLOWED_HOSTS = ['*']
else:
    if SERVER_MODE == DEVELOPMENT:
        ALLOWED_HOSTS = ['*']
    else:
        ALLOWED_HOSTS = [
            "localhost",
            ".media.mit.edu",
            ".media.mit.edu.",
        ]

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Databases

if SERVER_TYPE == LEAF:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            'TEST': {
                'SERIALIZE': False,
            }
        }
    }
else:
    if 'test' in sys.argv:
        # TODO: Setup a database for every possible layout
        raise NotImplementedError()
    else:
        # TODO: Setup a database for every registered farm
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            },
        }
        raise NotImplementedError()
CONN_MAX_AGE = None

# Caching

if SERVER_TYPE == LEAF:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
    SOLO_CACHE = 'default'
    SOLO_CACHE_TIMEOUT = 60
else:
    raise NotImplementedError()

# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(pathname)s %(lineno)d ' +
                      '%(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
        'verbose_request': {
            'format': '%(levelname)s %(asctime)s %(pathname)s %(lineno)d ' +
                      '%(status_code)d %(message)s %(request)s'
        },
        'simple_request': {
            'format': '%(levelname)s %(status_code)d %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'console_request': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'simple_request'
        },
        'log_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': '',
        },
        'log_file_request': {
            'level': 'WARNING', # We only care about 4xx's and 5xx's
            'class': 'logging.FileHandler',
            'formatter': 'verbose_request',
            'filename': '',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': '',
        },
        'error_file_request': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'formatter': 'verbose_request',
            'filename': '',
        },
    },
    'loggers': {
        'gro_api': {
            'handlers': ['log_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['log_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'django.request': {
            'handlers': ['log_file_request', 'error_file_request'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

if SERVER_MODE == DEVELOPMENT:
    debug_filename = os.path.join(BASE_DIR, 'debug.log')
    error_filename = os.path.join(BASE_DIR, 'error.log')
    LOGGING['handlers']['log_file']['filename'] = debug_filename
    LOGGING['handlers']['log_file_request']['filename'] = debug_filename
    LOGGING['handlers']['error_file']['filename'] = error_filename
    LOGGING['handlers']['error_file_request']['filename'] = error_filename
    LOGGING['loggers']['gro_api']['handlers'].append('console')
    LOGGING['loggers']['django.security']['handlers'].append('console')
    LOGGING['loggers']['django.request']['handlers'].append('console_request')
else:
    debug_filename = '/var/log/gro_api/debug.log'
    error_filename = '/var/log/gro_api/error.log'
    LOGGING['handlers']['log_file']['level'] = 'INFO'
    LOGGING['handlers']['log_file']['filename'] = debug_filename
    LOGGING['handlers']['log_file_request']['filename'] = debug_filename
    LOGGING['handlers']['error_file']['filename'] = error_filename
    LOGGING['handlers']['error_file_request']['filename'] = error_filename

# Testing

TEST_RUNNER = 'gro_api.gro_api.test.TestRunner'

REST_FRAMEWORK['TEST_REQUEST_DEFAULT_FORMAT'] = 'json'

# Cron

CRON_CLASSES = (
    'gro_api.farms.cron.UpdateFarmIp',
)

# Sites

SITE_ID = 1

# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = False

USE_TZ = True

# Secret Key

SECRET_FILE = os.path.join(BASE_DIR, 'secret.txt')
try:
    SECRET_KEY = open(SECRET_FILE).read().strip()
except IOError:
    try:
        import random
        VALID_CHARACTERS = "{}{}{}".format(
            string.ascii_letters,
            string.digits,
            string.punctuation,
        )
        CHARACTER = lambda: random.SystemRandom().choice(VALID_CHARACTERS)
        SECRET_KEY = ''.join([CHARACTER() for i in range(50)])
        SECRET = open(SECRET_FILE, 'w')
        SECRET.write(SECRET_KEY)
        SECRET.close()
    except IOError:
        raise Exception(
            'Failed to write secret key to secret file at '
            '{}'.format(SECRET_FILE)
        )
