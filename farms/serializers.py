from rest_framework import serializers
from .models import Farm

class FarmSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model  = Farm
        fields = ('url', 'farm_id', 'name', 'subdomain', 'layout', 'ip')
