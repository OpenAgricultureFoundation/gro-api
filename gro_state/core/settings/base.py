"""
Django settings for the gro-state project
"""
import sys
import django

# Patch django.setup to call our monkey-patching scripts
old_setup = django.setup
if not getattr(old_setup, 'is_patched', False):
    def my_setup():
        if not getattr(my_setup, 'has_run', False):
            from gro_state.core.handler import patch_handler
            from gro_state.core.disable_patch import disable_patch
            patch_handler()
            disable_patch()
        my_setup.has_run = True
        old_setup()
    my_setup.is_patched = True
    django.setup = my_setup

### General globals

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS': 'gro_state.core.pagination.Pagination',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ),
    'EXCEPTION_HANDLER': 'gro_state.core.views.exception_handler',
    'PAGE_SIZE': 100,
}

### Installed Apps

GRO_STATE_APPS = (
    'gro_state.farms',
    # 'gro_state.layout',
    # 'gro_state.plants',
    # 'gro_state.resources',
    # 'gro_state.sensors',
    # 'gro_state.actuators',
    # 'gro_state.recipes',
)

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
    'rest_framework_swagger',
    # Authentication apps
    'rest_framework.authtoken',
    'rest_auth',
    'allauth',
    'allauth.account',
    'rest_auth.registration',
)

### Request Handling

WSGI_APPLICATION = 'gro_state.core.wsgi.application'

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

STATIC_URL = '/static/'

MEDIA_URL = '/media/'

ALLOWED_HOSTS = ['*']

### Databases

CONN_MAX_AGE = None

### Caching

# This prevents cached singletons from carrying over between tests. There is a
# nice ticket in Django that would fix this problem more elegantly
# (https://code.djangoproject.com/ticket/11505), but this works for now
if 'test' in sys.argv:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'uwsgicache.UWSGICache',
        }
    }
SOLO_CACHE = 'default'
SOLO_CACHE_TIMEOUT = 60

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
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple_request'
        },
    },
    'loggers': {
        'gro_state': {
            'handlers': [],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.security': {
            'handlers': [],
            'level': 'DEBUG',
            'propagate': False
        },
        'django.request': {
            'handlers': [],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

### Testing

REST_FRAMEWORK['TEST_REQUEST_DEFAULT_FORMAT'] = 'json'

### Sites

SITE_ID = 1

### Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = False

USE_TZ = True
