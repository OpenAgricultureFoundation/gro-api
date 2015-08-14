from .views import (
    PlantModelViewSet, PlantTypeViewSet, PlantViewSet, SowEventViewSet,
    TransferEventViewSet, HarvestEventViewSet, PlantCommentViewSet
)

def contribute_to_router(router):
    router.register(r'plantModel', PlantModelViewSet)
    router.register(r'plantType', PlantTypeViewSet)
    router.register(r'plant', PlantViewSet)
    router.register(r'sowEvent', SowEventViewSet)
    router.register(r'transferEvent', TransferEventViewSet)
    router.register(r'harvestEvent', HarvestEventViewSet)
    router.register(r'plantComment', PlantCommentViewSet)
