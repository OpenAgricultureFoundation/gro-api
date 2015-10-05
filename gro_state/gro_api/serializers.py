"""
This module defines a set of classes that together allow models in this project
to be serialized correctly.
"""
import logging
from rest_framework.settings import api_settings
from rest_framework.relations import HyperlinkedRelatedField
from rest_framework.serializers import HyperlinkedModelSerializer
from rest_framework.utils.field_mapping import (
    get_detail_view_name, get_relation_kwargs, get_nested_relation_kwargs
)
from .utils import LayoutDependentAttribute

logger = logging.getLogger(__name__)

class BaseSerializer(HyperlinkedModelSerializer):
    """
    Base class used for all serializers in this project.
    """
    _fields = LayoutDependentAttribute('fields')

    def get_default_field_names(self, declared_fields, model_info):
        return (
            [api_settings.URL_FIELD_NAME] +
            list(declared_fields.keys()) +
            list(model_info.fields.keys()) +
            list(model_info.forward_relations.keys()) +
            list(model_info.reverse_relations.keys())
        )

    def build_field(self, field_name, info, model_class, nested_depth):
        if field_name in info.fields_and_pk:
            model_field = info.fields_and_pk[field_name]
            return self.build_standard_field(field_name, model_field)
        elif field_name in info.relations:
            relation_info = info.relations[field_name]
            if not nested_depth:
                field_class, field_kwargs = self.build_relational_field(
                    field_name, relation_info
                )
            else:
                field_class, field_kwargs = self.build_nested_field(
                    field_name, relation_info, nested_depth
                )
            # TODO: Make sure this actually does something
            # Don't allow writes to relations resulting from foreign keys
            # pointing to this class
            if relation_info.model_field is None:
                field_kwargs['read_only'] = True
                if 'queryset' in field_kwargs:
                    field_kwargs.pop('queryset')
            return field_class, field_kwargs
        elif hasattr(model_class, field_name):
            return self.build_property_field(field_name, model_class)
        elif field_name == api_settings.URL_FIELD_NAME:
            return self.build_url_field(field_name, model_class)
        return self.build_unknown_field(field_name, model_class)

    def build_relational_field(self, field_name, relation_info):
        field_class = self.serializer_related_field
        field_kwargs = get_relation_kwargs(field_name, relation_info)

        # `view_name` is only valid for hyperlinked relationships.
        if not issubclass(field_class, SmartHyperlinkedRelatedField) and \
                not issubclass(field_class, HyperlinkedRelatedField):
            field_kwargs.pop('view_name', None)
        field_kwargs['model_field'] = relation_info.model_field

        return field_class, field_kwargs

    def build_nested_field(self, field_name, relation_info, nested_depth):
        class NestedSerializer(BaseSerializer):
            class Meta:
                model = relation_info.related_model
                depth = nested_depth - 1

        field_class = NestedSerializer
        field_kwargs = get_nested_relation_kwargs(relation_info)

        return field_class, field_kwargs
