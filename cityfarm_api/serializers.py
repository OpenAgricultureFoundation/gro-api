from rest_framework import serializers
from rest_framework.utils.field_mapping import get_nested_relation_kwargs

class TreeSerializer(serializers.HyperlinkedModelSerializer):
    """
    A ModelSerializer subclass that is used for serializing objects in the
    layout tree. The ModelSerializer uses NestedSerializers for all references
    in each node. TreeSerializer will use NestedSerializers for the 'children'
    field but not the 'parent' field, which prevents us from returning redundant
    data in the serialized response.
    """
    def get_field_names(self, declared_fields, info):
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
            class NestedSerializer(TreeSerializer):
                class Meta:
                    model = relation_info.related_model
                    depth = nested_depth - 1
            field_class = NestedSerializer
            field_kwargs = get_nested_relation_kwargs(relation_info)

            return field_class, field_kwargs
        else:
            return super().build_nested_field(field_name, relation_info,
                    nested_depth)
