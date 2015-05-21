from rest_framework import viewsets
from plants.models import PlantSite
from plants.serializers import PlantSiteSerializer

class PlantSiteViewset(viewsets.ModelViewSet):
    queryset = PlantSite.objects.all()
    serializer_class = PlantSiteSerializer
