"""
This module defines a set of classes that together allow models in this project
to be serialized correctly.
"""
import logging
import importlib
from django.conf import settings
from rest_framework.settings import api_settings
from rest_framework.relations import HyperlinkedRelatedField
from rest_framework.serializers import (
    HyperlinkedModelSerializer, ValidationError
)
from rest_framework.utils.field_mapping import (
    get_detail_view_name, get_relation_kwargs, get_nested_relation_kwargs
)
from .utils import LayoutDependentAttribute

logger = logging.getLogger(__name__)

# HyperlinkedRelatedField.__init__ requires view_name != None, so we pass this
# constant in and ignore it in the setter for view_name
DUMMY_VIEW_NAME = 'dummy_view_name'

class DynamicHyperlinkedRelatedField(HyperlinkedRelatedField):
    """
    :class:`~rest_framework.HyperlinkedRelatedField` subclass that works for
    dynamic ForeignKey fields. The :attr:`queryset` and :attr:`view_name`
    attributes are dynamically read from the related field and have dummy
    setters so as not to break :meth:`HyperlinkedRelatedField.__init__`
    """
    def __init__(self, model_field, **kwargs):
        # Store the field so that we can dynamically get the queryset and
        # view_name from it
        self.model_field = model_field
        self.read_only = kwargs.get('read_only', False)
        kwargs['queryset'] = None
        kwargs['view_name'] = DUMMY_VIEW_NAME
        super().__init__(**kwargs)

    @property
    def view_name(self):
        return get_detail_view_name(self.model_field.related_model)

    @view_name.setter
    def view_name(self, val):
        # We should never be assigning an actual value to this property
        assert val == DUMMY_VIEW_NAME

    @property
    def queryset(self):
        if self.read_only:
            return None # So RelatedField.__init__ doesn't complain
        return self.model_field.related_model._default_manager.all()

    @queryset.setter
    def queryset(self, val):
        # We should never be assigning an actual value to this property
        assert val is None


class SmartHyperlinkedRelatedField:
    """
    A class that encapsulates a :class:`DynamicHyperlinkedRelatedField` if it's
    related field is dynamic and encapsulates a
    :class:`~rest_framework.relations.HyperlinkedRelatedField` otherwise.
    """
    def __init__(self, model_field, **kwargs):
        if getattr(model_field, 'is_dynamic', False):
            self.field = DynamicHyperlinkedRelatedField(model_field, **kwargs)
        else:
            self.field = HyperlinkedRelatedField(**kwargs)
    def __getattribute__(self, name):
        if name == 'field':
            return object.__getattribute__(self, 'field')
        else:
            return getattr(object.__getattribute__(self, 'field'), name)
    def __setattribute__(self, name, val):
        if name == 'field':
            object.__getattribute__(self, '__dict__')['field'] = val
        else:
            return setattr(object.__getattribute__(self, 'field'), name, val)


class BaseSerializer(HyperlinkedModelSerializer):
    """
    Base class used for all serializers in this project.
    """
    _fields = LayoutDependentAttribute('fields')
    serializer_related_field = SmartHyperlinkedRelatedField

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
