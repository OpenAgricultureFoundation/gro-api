"""
This module defines a set of classes that together allow models in this project
to be serialized correctly.
"""
import logging
import importlib
from django.conf import settings
from rest_framework import serializers
from rest_framework.settings import api_settings
from rest_framework.relations import HyperlinkedRelatedField
from rest_framework.serializers import (
    SerializerMetaclass
)
from rest_framework.utils.field_mapping import (
    get_detail_view_name, get_relation_kwargs, get_nested_relation_kwargs
)
from .utils import ModelDict

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
    def queryset(self):
        if self.read_only:
            return None # So RelatedField.__init__ doesn't complain
        return self.model_field.related_model._default_manager.all()

    @queryset.setter
    def queryset(self, val):
        # We should never be assigning an actual value to this property
        assert val == None

    @property
    def view_name(self):
        return get_detail_view_name(self.model_field.related_model)

    @view_name.setter
    def view_name(self, val):
        # We should never be assigning an actual value to this property
        assert val == DUMMY_VIEW_NAME

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

class SerializerRegistry(ModelDict):
    """
    A registry that keeps track of all of the serializer that have been
    registered for this project. :class:`BaseSerializer` will read from the
    registry when determining what serializer to use for nested relations. By
    default, :class:`BaseSerializer` is used.
    """
    def register(self, serializer):
        try:
            # This may fail if serializer is abstract, such as BaseSerializer
            self[serializer.Meta.model] = serializer
        except:
            pass

    def get_for_model(self, model):
        """
        Gets the serializer associated with the model `model`. If no serializer
        has been registered for the model, returns a :class:`BaseSerializer`
        subclass that can operate on the given model.
        """
        if not model in self:
            _model = model # Scoping is weird
            class Serializer(BaseSerializer): # pylint: disable=used-before-assignment
                class Meta:
                    model = _model
            self[model] = Serializer
        return self[model]

model_serializers = SerializerRegistry()

class MySerializerMetaclass(SerializerMetaclass):
    """
    Modify :class:`~rest_framework.serializer.SerializerMetaclass` to also
    provide default values for a set of attributes on the Meta and automatically
    register the serializer with `model_serializers`.
    """
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        meta_defaults = {
            'extra_fields': (),
            'nest_if_recursive': (),
            'never_nest': (),
            'models_already_nested': set(),
        }
        if 'Meta' in attrs:
            meta = attrs['Meta']
            for attr_name, attr_val in meta_defaults.items():
                if getattr(meta, attr_name, None) is None:
                    setattr(meta, attr_name, attr_val)
            if hasattr(meta, 'model'):
                model_key = model_serializers.get_key_for_model(meta.model)
                meta.models_already_nested.add(model_key)
            meta.models_being_nested = set()
        model_serializers.register(cls)

class BaseSerializer(serializers.HyperlinkedModelSerializer,
                     metaclass=MySerializerMetaclass):
    """
    Base class used for all serializers in this project.
    """
    serializer_related_field = SmartHyperlinkedRelatedField

    def __init__(self, *args, **kwargs):
        # We can't access self.context until super().__init__ has been called,
        # but we can't pass is_recursive into into super().__init__, so we pop
        # is_recursive now and don't use it until later
        is_recursive = kwargs.pop('is_recursive', None)
        super().__init__(*args, **kwargs)
        request = self.context.get('request', None)
        if request:
            if 'depth' in request.query_params:
                val = request.query_params['depth']
                try:
                    val = int(val)
                except TypeError:
                    self.Meta.depth = 0
                else:
                    val = min(max(val, 0), 10)
                    self.Meta.depth = val
            else:
                self.Meta.depth = 0
            self.is_recursive = self.Meta.depth > 0
        else:
            self.is_recursive = is_recursive

    def get_default_field_names(self, declared_fields, model_info):
        return (
            [api_settings.URL_FIELD_NAME] +
            list(declared_fields.keys()) +
            list(model_info.fields.keys()) +
            list(model_info.forward_relations.keys()) +
            list(model_info.reverse_relations.keys())
        )

    def get_field_names(self, declared_fields, info):
        field_names = tuple(super().get_field_names(declared_fields, info))
        return field_names + self.Meta.extra_fields

    def build_field(self, field_name, info, model_class, nested_depth):
        if self.is_recursive and field_name in self.Meta.nest_if_recursive:
            relation_info = info.relations[field_name]
            field_class, field_kwargs = self.build_nested_field(
                field_name,
                relation_info,
                max(nested_depth, 1)
            )
        elif field_name in info.fields_and_pk:
            model_field = info.fields_and_pk[field_name]
            field_class, field_kwargs = self.build_standard_field(
                field_name, model_field
            )
        elif field_name in info.relations:
            relation_info = info.relations[field_name]
            to_model_key = model_serializers.get_key_for_model(
                relation_info.related_model
            )
            if not nested_depth or field_name in self.Meta.never_nest or \
                    to_model_key in self.Meta.models_already_nested:
                field_class, field_kwargs = self.build_relational_field(
                    field_name, relation_info
                )
            else:
                field_class, field_kwargs = self.build_nested_field(
                    field_name, relation_info, nested_depth
                )
            # Don't allow writes to relations resulting from foreign keys
            # pointing to this class
            if relation_info.model_field is None:
                field_kwargs['read_only'] = True
                if 'queryset' in field_kwargs:
                    field_kwargs.pop('queryset')
        elif hasattr(model_class, field_name):
            field_class, field_kwargs = self.build_property_field(
                field_name, model_class
            )
        elif field_name == api_settings.URL_FIELD_NAME:
            field_class, field_kwargs = self.build_url_field(
                field_name, model_class
            )
        else:
            field_class, field_kwargs = self.build_unknown_field(
                field_name, model_class
            )
        # Disable writes in recursive queries
        if self.is_recursive:
            field_kwargs['read_only'] = True
            if 'queryset' in field_kwargs:
                field_kwargs.pop('queryset')
        return field_class, field_kwargs

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
        NestedBase = model_serializers.get_for_model(
            relation_info.related_model
        )
        class NestedSerializer(NestedBase):
            class Meta(getattr(NestedBase, 'Meta', object)):
                model = relation_info.related_model
                depth = nested_depth - 1
                models_already_nested = self.Meta.models_already_nested.copy()
        field_class = NestedSerializer
        field_kwargs = get_nested_relation_kwargs(relation_info)
        field_kwargs['is_recursive'] = self.is_recursive
        return field_class, field_kwargs

# Populate the serializer registry by making sure all serializer modules in this
# project have been imported
for app_name in settings.CITYFARM_API_APPS:
    try:
        importlib.import_module('.serializers', app_name)
    except ImportError as err:
        logger.info(err)
