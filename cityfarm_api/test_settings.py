from .settings import *
LOGGING['loggers'] = {}
if SERVER_TYPE == LEAF:
    MOCK_SYSTEM_LAYOUT = 'tray'
