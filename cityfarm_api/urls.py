import copy
import warnings
import functools
import importlib
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from .routers import HybridRouter
import control
import farms
import layout
import plants

#: A list of all of the apps from which to include API urls
cityfarm_api_apps = [control, farms, layout, plants]

# Construct a base_router containing all of the routes that don't change across
# farm layouts
base_router = HybridRouter()
for app in cityfarm_api_apps:
    app.urls = importlib.import_module('.urls', app.__package__)
    if hasattr(app.urls, 'register_static_patterns'):
        app.urls.register_static_patterns(base_router)
    else:
        warnings.warn(
            'App {}.urls should define function '
            '"register_static_patterns"'.format(app.__name__)
        )


@functools.lru_cache()
def urlconf_for_layout(layout):
    router = copy.deepcopy(base_router)
    for app in cityfarm_api_apps:
        if hasattr(app.urls, 'register_dynamic_patterns'):
            app.urls.register_dynamic_patterns(router, layout)
        else:
            warnings.warn(
                'App {} should define function '
                '"register_dynamic_patterns"'.format(app.__name__)
            )
    return router.urls + [
        url(r'^auth/', include('rest_framework.urls',
            namespace='rest_framework')),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.SERVER_TYPE == settings.LEAF:
    urlpatterns = urlconf_for_layout(farms.models.Farm.get_solo().layout)
