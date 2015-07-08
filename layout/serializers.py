"""
This module creates serializers for some of the models defines in the
layout.models module
"""
from rest_framework.serializers import ValidationError
from cityfarm_api.serializers import BaseSerializer
from layout.models import (
    Enclosure, Tray, dynamic_models, TrayLayout
)

class TrayLayoutSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = TrayLayout
    # TODO: Kwargs stuffs

class EnclosureSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = Enclosure
        nest_if_recursive = ('model',)

class LayoutObjectSerializer(BaseSerializer):
    """ A Serializer for subclasses of LayoutObject """
    class Meta(BaseSerializer.Meta):
        pass
    def validate_location(self, attrs):
        """ Ensure that this object fits inside it's parent """
        total_length = (attrs['x'] or 0) + (attrs['length'] or 0)
        parent_length = attrs['parent'].length
        if parent_length and not total_length <= parent_length:
            raise ValidationError("Model is too long to fit in its parent")
        total_width = (attrs['y'] or 0) + (attrs['width'] or 0)
        parent_width = attrs['parent'].width
        if parent_width and not total_width <= parent_width:
            raise ValidationError("Model is too wide to fit in its parent")
        total_height = (attrs['z'] or 0) + (attrs['height'] or 0)
        parent_height = attrs['parent'].height
        if parent_height and not total_height <= parent_height:
            raise ValidationError("Model is too tall to fit in its parent")
        return attrs
    def validate(self, attrs):
        return self.validate_location(attrs)

class TraySerializer(LayoutObjectSerializer):
    class Meta(LayoutObjectSerializer.Meta):
        model = Tray
        nest_if_recursive = ('model',)

    def create(self, validated_data):
        # TODO: Create plant sites here
        return super().create(validated_data)

for entity_name, entity_model in dynamic_models.items():
    class Serializer(LayoutObjectSerializer):
        class Meta(LayoutObjectSerializer.Meta):
            model = entity_model
            nest_if_recursive = ('model',)
