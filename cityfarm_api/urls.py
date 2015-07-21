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
