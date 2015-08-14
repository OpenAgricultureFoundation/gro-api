from django.conf import settings
from farms.models import Farm
from farms.serializers import FarmSerializer
if settings.SERVER_TYPE == settings.LEAF:
    from cityfarm_api.viewsets import SingletonModelViewSet as FarmViewSetBase
else:
    from rest_framework.viewsets import ModelViewSet as FarmViewSetBase


class FarmViewSet(FarmViewSetBase):
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    allow_on_unconfigured_farm = True
