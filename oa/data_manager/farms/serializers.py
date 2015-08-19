from rest_framework import serializers
from ..data_manager.serializers import BaseSerializer
from .models import Farm


class FarmSerializer(BaseSerializer):
    class Meta:
        model = Farm
