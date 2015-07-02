from cityfarm_api.viewsets import ModelViewSet
from plants.models import PlantSite, PlantType, Plant
from plants.serializers import (PlantSiteSerializer, PlantTypeSerializer,
PlantSerializer)

class PlantSiteViewset(ModelViewSet):
    queryset = PlantSite.objects.all()
    serializer_class = PlantSiteSerializer

class PlantTypeViewset(ModelViewSet):
    queryset = PlantType.objects.all()
    serializer_class = PlantTypeSerializer

class PlantViewset(ModelViewSet):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer
