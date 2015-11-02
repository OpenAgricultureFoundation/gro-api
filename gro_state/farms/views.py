from ..farms.models import Farm
from ..farms.serializers import FarmSerializer
from rest_framework.viewsets import ModelViewSet


class FarmViewSet(ModelViewSet):
    """ Represents a single physical OpenAg system """
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
