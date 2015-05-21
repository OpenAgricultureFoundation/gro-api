from rest_framework import serializers
from rest_framework.utils.field_mapping import get_nested_relation_kwargs

class BaseSerializer(serializers.HyperlinkedModelSerializer):
    # TODO: Describe these options
    """
    Base class used for all serializers in this project.
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
    def get_field_names(self, declared_fields, info):
        field_names = super().get_field_names(declared_fields,info)
        extra_fields = getattr(self.Meta, 'extra_fields', [])
        return field_names + extra_fields
    def build_nested_field(self, field_name, relation_info, nested_depth):
        never_nest = getattr(self.Meta, 'never_nest', [])
        extra_fields = getattr(self.Meta, 'extra_fields', [])
        if field_name in never_nest:
            return super().build_relational_field(field_name, relation_info)
        class NestedSerializer(BaseSerializer):
            class Meta:
                model = relation_info.related_model
                depth = nested_depth - 1
        NestedSerializer.Meta.never_nest = never_nest
        sub_extra_fields = [field for field in extra_fields if
                hasattr(NestedSerializer.Meta.model, field)]
        NestedSerializer.Meta.extra_fields = sub_extra_fields
        field_class = NestedSerializer
        field_kwargs = get_nested_relation_kwargs(relation_info)
        return field_class, field_kwargs
