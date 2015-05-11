from django.conf import settings

from farms.models import Farm
from farms.serializers import FarmSerializer

from cityfarm_api.viewsets import SingletonViewSet

class FarmViewSet(SingletonViewSet):
    model = Farm
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
