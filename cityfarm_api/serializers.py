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

    def create(self, validated_data):
        # TODO: I don't like having to override this
        raise_errors_on_nested_writes('create', self, validated_data)

        ModelClass = self.Meta.model

        # Remove many-to-many relationships from validated_data.
        # They are not valid arguments to the default `.create()` method,
        # as they require that the instance has already been saved.
        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        # Deal with DynamicForeignKey fields here for now because Django doesn't
        # realize that they are relations, so it doesn't know to extract the
        # model ID and assign it to the correct attribute (e.g. model.parent_id
        # = model.parent.pk). Hopefully we can find a better way to do that so
        # that Django actually sees our relations as relations
        fields_iter = iter(ModelClass._meta.concrete_fields)
        fields_hacked = {}
        for field in fields_iter:
            # Django is going to expect a pk and use field.attname as the key
            if isinstance(field, DynamicForeignKey):
                rel_obj = validated_data.pop(field.name)
                # Save the object so that we can repeat the assignment through
                # the descriptor after the object is created so it is cached.
                fields_hacked[field] = rel_obj
                validated_data[field.attname] = rel_obj.pk

        instance = ModelClass.objects.create(**validated_data)

        for field, obj in fields_hacked.items():
            setattr(instance, field.name, obj)

        # Save many-to-many relationships after the instance is created.
        if many_to_many:
            for field_name, value in many_to_many.items():
                setattr(instance, field_name, value)

        return instance

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
