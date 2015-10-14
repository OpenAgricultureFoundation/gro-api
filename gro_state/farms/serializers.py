from ..core.serializers import BaseSerializer
from .models import Farm

class FarmSerializer(BaseSerializer):
    class Meta:
        model = Farm
