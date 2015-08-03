from django.conf import settings
from farms.models import Farm
if settings.SERVER_TYPE == settings.LEAF:
    from cityfarm_api.viewsets import SingletonViewSet as FarmViewSetBase
else:
    from cityfarm_api.viewsets import ModelViewSet as FarmViewSetBase


class FarmViewSet(FarmViewSetBase):
    model = Farm
    allow_on_unconfigured_farm = True
