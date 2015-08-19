import logging
from django.conf import settings
from ..data_manager.utils import system_layout
from .views import (
    Model3DViewSet, TrayLayoutViewSet, PlantSiteLayoutViewSet,
    EnclosureViewSet, TrayViewSet, PlantSiteViewSet, dynamic_viewsets
)
from .schemata import all_schemata

logger = logging.getLogger(__name__)

def contribute_to_router(router):
    router.register('model3D', Model3DViewSet)
    router.register('trayLayout', TrayLayoutViewSet)
    router.register('plantSiteLayout', PlantSiteLayoutViewSet)
    router.register('enclosure', EnclosureViewSet)
    router.register('tray', TrayViewSet)
    router.register('plantSite', PlantSiteViewSet)
    current_layout = system_layout.current_value
    if settings.SERVER_TYPE == settings.ROOT and not current_layout:
        logger.error(
            'Root server encountered farm without layout. This should never '
            'happen'
        )
    if current_layout:
        for model_name in all_schemata[current_layout].dynamic_entities.keys():
            lower_model_name = model_name[0].lower() + model_name[1:]
            router.register(lower_model_name, dynamic_viewsets[model_name])
