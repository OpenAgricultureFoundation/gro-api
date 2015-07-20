"""
This module defines the set of urls to use for this project. In a leaf server,
this module defines a variable `urlpatterns` that Django automatically
interprets as the set of urls to use. For a root server, it defines a function
:func:`urlconf_for_layout` that can be used to get the set of urls to use for a
farm with some known layout.
"""
import copy
import warnings
import importlib
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from .routers import BaseRouter

def get_current_urls():
    return BaseRouter.get_instance().urls + [
        url(r'^auth/', include(
            'rest_framework.urls', namespace='rest_framework'
        )),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
