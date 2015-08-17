from rest_framework import serializers
from ..data_manager.serializers import BaseSerializer
from .models import LAYOUT_CHOICES, Farm


class FarmSerializer(BaseSerializer):
    class Meta:
        model = Farm

    name = serializers.CharField(max_length=100, required=True)
    layout = serializers.ChoiceField(choices=LAYOUT_CHOICES, required=True)
