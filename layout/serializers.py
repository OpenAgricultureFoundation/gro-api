from rest_framework.serializers import ValidationError
from rest_framework.utils.model_meta import _resolve_model
from rest_framework.utils.model_meta import get_field_info, RelationInfo
from rest_framework.utils.field_mapping import get_nested_relation_kwargs
from cityfarm_api.serializers import BaseSerializer
from layout.models import all_models
from layout.models import Model3D, TrayLayout, PlantSiteLayout
from layout.models import PositionMixin, SizeMixin

######################
# Static Serializers #
######################

class Model3DSerializer(BaseSerializer):
    class Meta:
        model = Model3D


class TrayLayoutSerializer(BaseSerializer):
    class Meta:
        model = TrayLayout
        fields = ("name", "plant_sites")
        depth = 1


class PlantSiteLayoutSerializer(BaseSerializer):
    class Meta:
        model = PlantSiteLayout


########################
# Modified Serializers #
########################

class LayoutObjectSerializer(BaseSerializer):
    """
    A ModelSerializers subclass taht is used for serializing LayoutObject
    """
    pass
    # TODO layout_object field that links to child object
    # layout_object = serializers.SerializerMethodField()
    # def get_layout_object(self, obj):
    #     return self.Meta.model.objects.get_subclass(pk=obj.pk)

class LayoutObjectSubSerializer(BaseSerializer):
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
        if issubclass(self.Meta.model, PositionMixin) and \
                issubclass(self.Meta.model, SizeMixin):
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
            return self.build_relational_field(field_name, relation_info)
        else:
            return super().build_field(field_name, info, model_class,
                    nested_depth)
    def create(self, validated_data):
        obj = super().create(validated_data)
        if "name" in validated_data and validated_data["name"] is "":
            obj.name = "{} {}".format(self.Meta.model_name, obj.pk)
            obj.save()
        return obj

class TraySerializer(LayoutObjectSubSerializer):
    def create(self, validated_data):
        print("Creating plant sites")
        return super().create(validated_data)

all_serializers = {}
for schema_name, curr_models in all_models.items():
    curr_serializers = {}
    for model_name, model in curr_models.items():
        if model_name == "layout_object":
            class Serializer(LayoutObjectSerializer):
                class Meta:
                    model = model
        elif model_name == "tray":
            class Serializer(TraySerializer):
                class Meta:
                    model = model
                    extra_fields = ["plant_sites"]
                    always_nest = ["model"]
                    never_nest = ["parent"]
        else:
            class Serializer(LayoutObjectSubSerializer):
                class Meta:
                    model = model
                    model_name = model_name
                    extra_fields = ["children"]
                    always_nest = ["model"]
                    never_nest = ["parent"]
        curr_serializers[model_name] = Serializer
    all_serializers[schema_name] = curr_serializers
