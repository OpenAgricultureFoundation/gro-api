from rest_framework import viewsets
from plants.models import PlantSite, PlantType, Plant
from plants.serializers import (PlantSiteSerializer, PlantTypeSerializer,
PlantSerializer)

class PlantSiteViewset(viewsets.ModelViewSet):
    queryset = PlantSite.objects.all()
    serializer_class = PlantSiteSerializer

class PlantTypeViewset(viewsets.ModelViewSet):
    queryset = PlantType.objects.all()
    serializer_class = PlantTypeSerializer

class PlantViewset(viewsets.ModelViewSet):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer
