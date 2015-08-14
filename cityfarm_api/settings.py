"""
Django settings for cityfarm_api project.
"""

import os
import sys
import string

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS': 'cityfarm_api.pagination.Pagination',
    'PAGE_SIZE': 100,
}

# Local Configuration

LEAF = "leaf"
ROOT = "root"

SERVER_TYPE = os.environ['CITYFARM_API_SERVER_TYPE']
if SERVER_TYPE not in [LEAF, ROOT]:
    raise ValueError('Invalid server type read from environment')

DEVELOPMENT = "development"
PRODUCTION = "production"

SERVER_MODE = os.environ['CITYFARM_API_SERVER_MODE']
if SERVER_MODE not in [DEVELOPMENT, PRODUCTION]:
    raise ValueError('Invalid server mode read from environment')

if SERVER_MODE == DEVELOPMENT:
    DEBUG = True
else:
    DEBUG = False

# Installed Apps

CITYFARM_API_APPS = (
    'farms',
    'layout',
    'plants',
    'resources',
    'sensors',
    'actuators',
    'recipes',
)

if SERVER_TYPE == LEAF:
    CITYFARM_API_APPS = CITYFARM_API_APPS + ('control',)

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
    'rest_framework.authtoken',
    'rest_auth',
    'allauth',
    'allauth.account',
    'rest_auth.registration',
)

if SERVER_MODE == DEVELOPMENT:
    FRAMEWORK_APPS += ('debug_toolbar',)
    DEBUG_TOOLBAR_PATCH_SETTINGS = False
    INTERNAL_IPS = ['127.0.0.1']

INSTALLED_APPS = CITYFARM_API_APPS + FRAMEWORK_APPS

# Request Handling

WSGI_APPLICATION = 'cityfarm_api.wsgi.application'

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
        'cityfarm_api.middleware.RequestCacheMiddleware',
        'cityfarm_api.middleware.FarmRoutingMiddleware',
    )
else:
    MIDDLEWARE_CLASSES += (
        'cityfarm_api.middleware.FarmIsConfiguredCheckMiddleware',
    )

if SERVER_MODE == DEVELOPMENT:
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = 'cityfarm_api.urls'

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
    DATABASE_ROUTERS = ['cityfarm_api.middleware.FarmDbRouter']

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'cityfarm_api', 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'cityfarm_api', 'media')

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
        'cityfarm_api': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}
for app_name in CITYFARM_API_APPS:
    LOGGING['loggers'][app_name] = {
        'handlers': ['file', ],
        'level': 'DEBUG',
        'propagate': True,
    }

if SERVER_MODE == DEVELOPMENT:
    LOGGING['handlers']['file']['filename'] = \
        os.path.join(BASE_DIR, 'debug.log')
    LOGGING['loggers']['cityfarm_api']['handlers'].append('console')
    for app_name in CITYFARM_API_APPS:
        LOGGING['loggers'][app_name]['handlers'].append('console')
else:
    LOGGING['handlers']['file']['level'] = 'INFO'
    LOGGING['handlers']['file']['filename'] = '/var/log/cityfarm_api.log'
if 'django.security' not in LOGGING['loggers']:
    LOGGING['loggers']['django.security'] = {
        'handlers': [],
    }
LOGGING['loggers']['django.security']['handlers'].append('file')
LOGGING['loggers']['django.security']['level'] = 'INFO'
if 'django.request' not in LOGGING['loggers']:
    LOGGING['loggers']['django.request'] = {
        'handlers': [],
    }
LOGGING['loggers']['django.request']['handlers'].append('file')
LOGGING['loggers']['django.request']['level'] = 'INFO'

# Testing

TEST_RUNNER = 'cityfarm_api.test.TestRunner'

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
