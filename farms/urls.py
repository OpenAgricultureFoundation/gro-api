from .views import FarmViewSet

def contribute_to_router(router):
    router.register(r'farm', FarmViewSet)
