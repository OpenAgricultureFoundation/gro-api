from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from .routers import BaseRouter

def get_current_urls():
    urls = BaseRouter.get_instance().urls + [
        url(r'^auth/', include('rest_auth.urls')),
        url(r'^auth/registration/', include('rest_auth.registration.urls')),
        url(r'^docs/', include('rest_framework_swagger.urls')),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if settings.DEBUG:
        import debug_toolbar
        urls.append(url(r'^__debug__/', include(debug_toolbar.urls)))
    return urls
