"""
WSGI config for cityfarm_api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import django
from django.core.handlers.wsgi import WSGIHandler

django.setup()

from layout import monkey_patch_resolvers

application = WSGIHandler()
