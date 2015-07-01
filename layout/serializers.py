from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.utils.model_meta import _resolve_model
from rest_framework.utils.model_meta import get_field_info, RelationInfo
from rest_framework.utils.field_mapping import get_nested_relation_kwargs
from plants.serializers import PlantSiteSerializer
from cityfarm_api.serializers import BaseSerializer
from layout.models import (
    Model3D, TrayLayout, PlantSiteLayout, LayoutObject, Enclosure, Tray,
    dynamic_models
)

class Model3DSerializer(BaseSerializer):
    class Meta:
        model = Model3D


class TrayLayoutSerializer(BaseSerializer):
    class Meta:
        model = TrayLayout


class PlantSiteLayoutSerializer(BaseSerializer):
    class Meta:
        model = PlantSiteLayout



class LayoutObjectSerializer(BaseSerializer):
    class Meta:
        model = LayoutObject
    layout_object = serializers.SerializerMethodField()
    def get_layout_object(self, obj):
        return self.Meta.model.objects.get_subclass()

class LayoutObjectSubSerializer(BaseSerializer):
    """
    A Serializer for subclasses of LayoutObject
    """
    def validate_location(self, attrs):
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
        if getattr(self.Meta, 'validate_location', False):
            return self.validate_location(attrs)
        else:
            return attrs
    def build_field(self, field_name, info, model_class, nested_depth):
        if field_name == "layout_object":
            model_field = model_class.layout_object.field
            relation_info = RelationInfo(
                model_field = model_field,
                related_model = _resolve_model(model_field.rel.to),
                to_many = False,
                has_through_model = True
            )
            return self.build_relational_field(
                field_name, relation_info
            )
        else:
            return super().build_field(field_name, info, model_class,
                    nested_depth)

dynamic_serializers = {}

class EnclosureSerializer(LayoutObjectSubSerializer):
    class Meta:
        model = Enclosure
        nest_if_recursive = ('model',)
        never_nest = ('parent', 'layout_object')
        nested_serializers = dynamic_serializers

class TraySerializer(LayoutObjectSubSerializer):
    class Meta:
        model = Tray
        extra_fields = ('plant_sites',)
        nest_if_recursive = ('model',)
        never_nest = ('parent', 'layout_object')
        nested_serializers = {'plantsite': PlantSiteSerializer}
    def create(self, validated_data):
        # TODO: Create plant sites here
        return super().create(validated_data)

class NestedTraySerializer(LayoutObjectSubSerializer):
    class Meta:
        model = Tray
        extra_fields = ('plant_sites',)
        nest_if_recursive = ('model',)
        never_nest = ('parent', 'layout_object', 'plant_sites')

for entity_name, entity_model in dynamic_models.items():
    class Serializer(LayoutObjectSubSerializer):
        class Meta:
            model = entity_model
            nest_if_recursive = ('model',)
            never_nest = ('parent', 'layout_object')
    dynamic_serializers[entity_name] = Serializer

nested_serializers = dynamic_serializers.copy()
nested_serializers.update({
    'tray': NestedTraySerializer,
})
for Serializer in dynamic_serializers.values():
    Serializer.Meta.nested_serializers = nested_serializers
