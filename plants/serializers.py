from cityfarm_api.serializers import BaseSerializer
from plants.models import PlantSite, PlantType, Plant

class PlantSerializer(BaseSerializer):
    class Meta:
        model = Plant
        extra_fields = ('plant_type', 'site')

class PlantSiteNestedPlantSerializer(BaseSerializer):
    class Meta:
        model = Plant
        extra_fields = ('site',)
        never_nest = ('site',)

class PlantTypeNestedPlantSerializer(BaseSerializer):
    class Meta:
        model = Plant
        extra_fields = ('site',)
        never_nest = ('site', 'plant_type')

class PlantSiteSerializer(BaseSerializer):
    class Meta:
        model = PlantSite
        extra_fields = ('plant',)
        never_nest = ('parent',)
        nested_serializers = {
            'plant': PlantSiteNestedPlantSerializer
        }

class PlantTypeSerializer(BaseSerializer):
    class Meta:
        model = PlantType
        extra_fields = ('plants',)
        never_nest = ('parent', 'plant_type')
        nested_serializers = {
            'plant': PlantTypeNestedPlantSerializer
        }
