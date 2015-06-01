from cityfarm_api.serializers import BaseSerializer
from plants.models import PlantSite, PlantType, Plant

class PlantSiteSerializer(BaseSerializer):
    class Meta:
        model = PlantSite

class PlantTypeSerializer(BaseSerializer):
    class Meta:
        model = PlantType

class PlantSerializer(BaseSerializer):
    class Meta:
        model = Plant
        always_nest = ["type"]
