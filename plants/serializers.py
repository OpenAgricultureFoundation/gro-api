from rest_framework import serializers
from plants.models import PlantSite

class PlantSiteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PlantSite
