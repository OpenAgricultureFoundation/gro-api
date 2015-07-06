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
import farms
import layout
import plants
import control
from .routers import HybridRouter
from .utils import get_current_layout

#: A list of all of the apps from which to include API urls
CITYFARM_API_APPS = [control, farms, layout, plants]

# Construct a base router containing all of the routes that don't change across
# farm layouts
BASE_ROUTER = HybridRouter()
for app in CITYFARM_API_APPS:
    app.urls = importlib.import_module('.urls', app.__package__)
    if hasattr(app.urls, 'register_static_patterns'):
        app.urls.register_static_patterns(BASE_ROUTER)
    else:
        warnings.warn(
            'App {}.urls should define function '
            '"register_static_patterns"'.format(app.__name__)
        )


def urlconf_for_layout(layout):
    """
    Returns a router defining the set of urls to use for a farm with the given
    layout.

    :param str layout: The farm layout for which to generate a url router
    """
    router = copy.deepcopy(BASE_ROUTER)
    for app in CITYFARM_API_APPS:
        if hasattr(app.urls, 'register_dynamic_patterns'):
            app.urls.register_dynamic_patterns(router, layout)
        else:
            warnings.warn(
                'App {} should define function '
                '"register_dynamic_patterns"'.format(app.__name__)
            )
    return router.urls + [
        url(r'^auth/', include(
            'rest_framework.urls', namespace='rest_framework'
        )),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.SERVER_TYPE == settings.ROOT:
    import functools
    urlconf_for_layout = functools.lru_cache()(urlconf_for_layout)

if settings.SERVER_TYPE == settings.LEAF:
    urlpatterns = urlconf_for_layout(get_current_layout())
