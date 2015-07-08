from cityfarm_api.viewsets import model_viewsets
from layout.models import Model3D, Tray, Enclosure, dynamic_models
from .schemata import all_schemata

def register_static_patterns(router):
    router.register(r'model3D', model_viewsets.get_for_model(Model3D))
    # router.register(r'trayLayout', views.TrayLayoutViewSet)
    # router.register(r'plantSiteLayout', views.PlantSiteLayoutViewSet)

def register_dynamic_patterns(router, layout):
    router.register(r'enclosure', model_viewsets.get_for_model(Enclosure))
    router.register(r'tray', model_viewsets.get_for_model(Tray))
    schema = all_schemata[layout]
    for entity in schema.dynamic_entities.values():
        curr_model = dynamic_models[entity.name]
        curr_viewset = model_viewsets.get_for_model(curr_model)
        router.register(entity.name.lower(), curr_viewset)
