from ..farms.models import Farm
from ..farms.serializers import FarmSerializer
from ..gro_api.viewsets import SingletonModelViewSet


class FarmViewSet(SingletonModelViewSet)
    """ Represents a single Personal Food Computer """
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
