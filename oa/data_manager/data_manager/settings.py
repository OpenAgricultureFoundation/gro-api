"""
Django settings for OA Data Manager project.
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
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS': 'oa.data_manager.data_manager.pagination.Pagination',
    'PAGE_SIZE': 100,
}

# Local Configuration

LEAF = "leaf"
ROOT = "root"

DEVELOPMENT = "development"
PRODUCTION = "production"

try:
    SERVER_TYPE = os.environ['OA_DATA_MANAGER_SERVER_TYPE']
    SERVER_MODE = os.environ['OA_DATA_MANAGER_SERVER_MODE']
except KeyError:
    raise ImproperlyConfigured(
        'Run oa_data_manager_configure before attempting to run anything.'
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

OA_DATA_MANAGER_APPS = (
    'oa.data_manager.farms',
    'oa.data_manager.layout',
    'oa.data_manager.plants',
    'oa.data_manager.resources',
    'oa.data_manager.sensors',
    'oa.data_manager.actuators',
    'oa.data_manager.recipes',
)

if SERVER_TYPE == LEAF:
    OA_DATA_MANAGER_APPS = OA_DATA_MANAGER_APPS + ('oa.data_manager.control',)

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
    'rest_auth.registration',
    'rest_framework_swagger',
)

if SERVER_MODE == DEVELOPMENT:
    FRAMEWORK_APPS += ('debug_toolbar',)
    DEBUG_TOOLBAR_PATCH_SETTINGS = False
    INTERNAL_IPS = ['127.0.0.1']

INSTALLED_APPS = OA_DATA_MANAGER_APPS + FRAMEWORK_APPS

# Request Handling

WSGI_APPLICATION = 'oa.data_manager.data_manager.wsgi.application'

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
        'oa.data_manager.data_manager.middleware.RequestCacheMiddleware',
        'oa.data_manager.data_manager.middleware.FarmRoutingMiddleware',
    )
else:
    MIDDLEWARE_CLASSES += (
        'oa.data_manager.data_manager.middleware.FarmIsConfiguredCheckMiddleware',
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
    DATABASE_ROUTERS = ['oa.data_manager.middleware.FarmDbRouter']

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'data_manager', 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'oa/data_manager', 'media')

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
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG' if SERVER_MODE == DEVELOPMENT else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': '',
        },
    },
    'loggers': {
        'oa.data_manager': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

if SERVER_MODE == DEVELOPMENT:
    LOGGING['handlers']['file']['filename'] = \
        os.path.join(BASE_DIR, 'debug.log')
    LOGGING['loggers']['oa.data_manager']['handlers'].append('console')
else:
    LOGGING['handlers']['file']['level'] = 'INFO'
    LOGGING['handlers']['file']['filename'] = '/var/log/oa_data_manager.log'
if 'django.security' not in LOGGING['loggers']:
    LOGGING['loggers']['django.security'] = {
        'handlers': [],
        'level': 'INFO',
    }
if 'handlers' not in LOGGING['loggers']['django.security']:
    LOGGING['loggers']['django.security']['handlers'] = []
LOGGING['loggers']['django.security']['handlers'].append('file')
LOGGING['loggers']['django.security']['level'] = 'INFO'
if 'django.request' not in LOGGING['loggers']:
    LOGGING['loggers']['django.request'] = {
        'handlers': [],
        'level': 'INFO',
    }
if 'handlers' not in LOGGING['loggers']['django.request']:
    LOGGING['loggers']['django.request']['handlers'] = []
LOGGING['loggers']['django.request']['handlers'].append('file')
LOGGING['loggers']['django.request']['level'] = 'INFO'

# Testing

TEST_RUNNER = 'oa.data_manager.data_manager.test.TestRunner'

REST_FRAMEWORK['TEST_REQUEST_DEFAULT_FORMAT'] = 'json'

# Cron

CRON_CLASSES = (
    'farms.cron.UpdateFarmIp',
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
