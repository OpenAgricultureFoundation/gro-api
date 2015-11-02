from .views import FarmViewSet

def contribute_to_router(router, layout):
    if layout is None:
        router.register(r'farm', FarmViewSet)
