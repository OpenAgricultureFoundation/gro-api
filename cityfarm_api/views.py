from cityfarm_api.models import Farm
from cityfarm_api.serializers import FarmSerializer

from rest_framework import viewsets

if settings.NODE_TYPE == "ROOT":
    farm_queryset = Farm.objects.all()
elif settings.NODE_TYPE == "LEAF":
    farm_queryset = Farm.get_solo()

class FarmViewset(viewsets.ModelViewSet):
    queryset = farm_queryset
    serializer_class = FarmSerializer
