"""
WSGI config for OA Data Manager project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""
import os
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from ..scripts.load_env import load_env

settings_module = 'gro_api.gro_api.settings'
os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
load_env()

application = get_wsgi_application()

# Send a fake request to the server right after it is created to make it less
# lazy
from django.test import RequestFactory

fake_environ = RequestFactory().get('/').environ
fake_start_response = lambda x, y: None
application(fake_environ, fake_start_response)
