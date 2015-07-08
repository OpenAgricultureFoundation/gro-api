from cityfarm_api.viewsets import ModelViewSet
from plants.models import PlantSite, PlantType, Plant

class PlantSiteViewSet(ModelViewSet):
    model = PlantSite

class PlantTypeViewSet(ModelViewSet):
    model = PlantType

class PlantViewSet(ModelViewSet):
    model = Plant
