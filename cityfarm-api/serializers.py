from rest_framework import serializers
from farm.models import Farm

class FarmSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model  = Farm
        fields = ('url', 'name', 'subdomain', 'layout', 'ip')
