from .views import FarmViewSet

def contribute_to_router(router, layout):
    if layout is None:
        router.register(r'farm', FarmViewSet)
    # if layout is None:
    #     urls = urls + [
    #         url(r'^auth/', include('rest_auth.urls')),
    #         url(r'^auth/registration/', include('rest_auth.registration.urls')),
    #         url(r'^docs/', include('rest_framework_swagger.urls')),
    #     ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
