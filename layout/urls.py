import logging
from django.conf import settings
from cityfarm_api.utils.state import system_layout
from .models import (
    Model3D, TrayLayout, PlantSiteLayout, LayoutObject, Enclosure, Tray,
    PlantSite, dynamic_models
)
from .schemata import all_schemata

logger = logging.getLogger(__name__)

def contribute_to_router(router):
    router.register_model(Model3D)
    router.register_model(TrayLayout)
    router.register_model(PlantSiteLayout)
    router.register_model(LayoutObject)
    router.register_model(Enclosure)
    router.register_model(Tray)
    router.register_model(PlantSite)
    current_layout = system_layout.current_value
    if settings.SERVER_TYPE == settings.ROOT and not current_layout:
        logger.warn(
            'Root server encountered farm without layout. This should never '
            'happen'
        )
    if current_layout:
        for model_name in all_schemata[current_layout].dynamic_entities.keys():
            router.register_model(dynamic_models[model_name])
