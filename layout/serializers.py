from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.utils.field_mapping import get_nested_relation_kwargs
from layout.models import all_models, LocationMixin, Model3D

class Model3DSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Model3D

class LayoutObjectSerializer(serializers.HyperlinkedModelSerializer):
    """
    A ModelSerializer subclass that is used for serializing LayoutObjects. The
    ModelSerializers be default uses NestedSerializers for all references in
    each node when the depth parameter of the meta class is supplied.
    LayoutObjectSerializer uses NestedSerializers for the 'children' field but
    not the 'parent' field, which prevents us from returning redundant data in
    the serialized response.
    """
    def validate_location(self, attrs):
        total_width = (attrs['x'] or 0) + (attrs['width'] or 0)
        parent_width = attrs['parent'].width
        if parent_width and not total_width <= parent_width:
            raise ValidationError("Model is too wide to fit in its parent")
        total_length = (attrs['y'] or 0) + (attrs['length'] or 0)
        parent_length = attrs['parent'].length
        if parent_length and not total_length <= parent_length:
            raise ValidationError("Model is too long to fit in its parent")
        total_height = (attrs['z'] or 0) + (attrs['height'] or 0)
        parent_height = attrs['parent'].height
        if parent_height and not total_height <= parent_height:
            raise ValidationError("Model is too tall to fit in its parent")
        return attrs
    def validate(self, attrs):
        if issubclass(self.Meta.model, LocationMixin):
            return self.validate_location(attrs)
        else:
            return attrs
    def get_field_names(self, declared_fields, info):
        """
        Add the "children" field to the list of fields to serialize if it exists
        in the model.
        """
        field_names = super().get_field_names(declared_fields, info)
        if hasattr(self.Meta.model, 'children'):
            if isinstance(field_names, tuple):
                field_names = field_names + ('children',)
            elif isinstance(field_names, list):
                field_names.append('children')
            else:
                raise TypeError()
        return field_names
    def build_nested_field(self, field_name, relation_info, nested_depth):
        if field_name == "parent":
            return self.build_relational_field(field_name, relation_info)
        elif field_name == "children":
            class NestedSerializer(LayoutObjectSerializer):
                class Meta:
                    model = relation_info.related_model
                    depth = nested_depth - 1
            field_class = NestedSerializer
            field_kwargs = get_nested_relation_kwargs(relation_info)
            return field_class, field_kwargs
        else:
            return super().build_nested_field(field_name, relation_info,
                    nested_depth)

all_serializers = {}
for schema_name, curr_models in all_models.items():
    curr_serializers = {}
    for model_name, model in curr_models.items():
        class Serializer(LayoutObjectSerializer):
            class Meta:
                model = model
        curr_serializers[model_name] = Serializer
    all_serializers[schema_name] = curr_serializers
