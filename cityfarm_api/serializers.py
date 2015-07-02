from rest_framework import serializers
from rest_framework.utils import model_meta
from rest_framework.settings import api_settings
from rest_framework.relations import HyperlinkedRelatedField
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils.field_mapping import (
    get_detail_view_name, get_relation_kwargs, get_nested_relation_kwargs
)

DUMMY_VIEW_NAME = 'dummy_view_name'

class DynamicHyperlinkedRelatedField(HyperlinkedRelatedField):
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
            return object.__setattribute__(self, 'field', val)
        else:
            return setattr(object.__getattribute__(self, 'field'), name, val)

class BaseSerializer(serializers.HyperlinkedModelSerializer):
    # TODO: Describe these options
    """
    Base class used for all serializers in this project.
    """
    serializer_related_field = SmartHyperlinkedRelatedField
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request', None)
        field_defaults = {
            'depth': 0,
            'extra_fields': (),
            'nest_if_recursive': (),
            'never_nest': (),
            'is_recursive': False,
            'nested_serializers': {},
        }
        if request:
            if 'depth' in request.query_params:
                val = request.query_params['depth']
                try:
                    val = int(val)
                except TypeError:
                    pass
                else:
                    val = min(max(val, 0), 10)
                    self.Meta.depth = val
            else:
                self.Meta.depth = field_defaults['depth']
            self.Meta.is_recursive = self.Meta.depth > 0
        for field_name, default in field_defaults.items():
            if not hasattr(self.Meta, field_name) or \
                    getattr(self.Meta, field_name) is None:
                setattr(self.Meta, field_name, default)

    def get_field_names(self, declared_fields, info):
        field_names = super().get_field_names(declared_fields, info)
        field_names = tuple(field_names)
        return field_names + self.Meta.extra_fields

    def build_field(self, field_name, info, model_class, nested_depth):
        if self.Meta.is_recursive and field_name in self.Meta.nest_if_recursive:
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
            if not nested_depth:
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
        if self.Meta.is_recursive:
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
        if field_name in self.Meta.never_nest:
            return super().build_relational_field(field_name, relation_info)
        field_class = self.build_nested_serializer_class(field_name,
                relation_info.related_model, nested_depth)
        field_kwargs = get_nested_relation_kwargs(relation_info)
        return field_class, field_kwargs

    # TODO: This can now be included in build_nested_field (I think)
    def build_nested_serializer_class(self, field_name, related_model, nested_depth):
        NestedBase = self.Meta.nested_serializers.get(related_model._meta.model_name, BaseSerializer)
        class NestedSerializer(NestedBase):
            class Meta(getattr(NestedBase, 'Meta', object)):
                model = related_model
                depth = nested_depth - 1
                is_recursive = self.Meta.is_recursive
        return NestedSerializer
