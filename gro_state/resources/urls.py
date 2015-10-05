from .views import (
    ResourceTypeViewSet, ResourcePropertyViewSet, ResourceEffectViewSet,
    ResourceViewSet
)

def contribute_to_router(router):
    router.register(r'resourceType', ResourceTypeViewSet)
    router.register(r'resourceProperty', ResourcePropertyViewSet)
    router.register(r'resourceEffect', ResourceEffectViewSet)
    router.register(r'resource', ResourceViewSet)
