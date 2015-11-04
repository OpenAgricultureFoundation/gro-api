from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from .routers import BaseRouter

def get_urls_by_layout(layout):
    urls = BaseRouter.get_instance(layout).urls
    # TODO: do we need this?
    # urls += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if settings.DEBUG:
        import debug_toolbar
        urls.append(url(r'^__debug__/', include(debug_toolbar.urls)))
    return [url(r'api/', include(urls)), ]
