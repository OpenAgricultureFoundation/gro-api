from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.utils.model_meta import _resolve_model
from rest_framework.utils.model_meta import get_field_info, RelationInfo
from rest_framework.utils.field_mapping import get_nested_relation_kwargs
from layout.models import all_models, LocationMixin, Model3D

class Model3DSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Model3D

class LayoutObjectSerializer(serializers.HyperlinkedModelSerializer):
    """
    A ModelSerializers subclass taht is used for serializing LayoutObject
    """
    pass
    # TODO layout_object field that links to child object
    # layout_object = serializers.SerializerMethodField()
    # def get_layout_object(self, obj):
    #     return self.Meta.model.objects.get_subclass(pk=obj.pk)

class LayoutObjectSubSerializer(serializers.HyperlinkedModelSerializer):
    """
    A ModelSerializer subclass that is used for serializing LayoutObjects. The
    ModelSerializers be default uses NestedSerializers for all references in
    each node when the depth parameter of the meta class is supplied.
    LayoutObjectSerializer uses NestedSerializers for the 'children' field but
    not the 'parent' field, which prevents us from returning redundant data in
    the serialized response.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request', None)
        if request:
            depth = request.query_params.get('depth', '0')
            try:
                depth = int(depth)
            except:
                depth = 0
            depth = min(max(depth, 0), 10)
            self.Meta.depth = depth
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
        Serialize all relations in the model, as well as the "layout_object"
        field.
        """
        field_names = super().get_field_names(declared_fields, info)
        relations = get_field_info(self.Meta.model).relations
        for field_name, relation_info in relations.items():
            field_names.append(field_name)
        if hasattr(self.Meta.model, "layout_object"):
            field_names.append("layout_object")
        return field_names
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
        if model_name == "layout_object":
            class Serializer(LayoutObjectSerializer):
                class Meta:
                    model = model
        else:
            class Serializer(LayoutObjectSubSerializer):
                class Meta:
                    model = model
        curr_serializers[model_name] = Serializer
    all_serializers[schema_name] = curr_serializers
