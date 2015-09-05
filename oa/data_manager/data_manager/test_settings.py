from .settings import *
SETUP_WITH_LAYOUT = None
LOGGING['handlers']['console']['level'] = 'WARNING'
# We're going to be causing some 4xx's on purpose, and we don't want django to
# complain every time
LOGGING['loggers']['django.request']['level'] = 'ERROR'
