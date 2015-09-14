from django.conf import settings
from ..gro_api.permissions import IsAdminOrReadOnly
from ..farms.models import Farm
from ..farms.serializers import FarmSerializer
if settings.SERVER_TYPE == settings.LEAF:
    from ..gro_api.viewsets import SingletonModelViewSet as FarmViewSetBase
else:
    from rest_framework.viewsets import ModelViewSet as FarmViewSetBase


class FarmViewSet(FarmViewSetBase):
    """ Represents a single Personal Food Computer """
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    permission_classes = [IsAdminOrReadOnly, ]
    allow_on_unconfigured_farm = True
