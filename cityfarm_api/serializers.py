from rest_framework import serializers
from rest_framework.utils import model_meta
from rest_framework.settings import api_settings
from rest_framework.relations import HyperlinkedRelatedField
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils.field_mapping import (
    get_detail_view_name, get_nested_relation_kwargs
)
from layout.fields import DynamicForeignKey, DynamicRelation

DUMMY_VIEW_NAME = 'dummy_view_name'

class DynamicForeignKeyField(HyperlinkedRelatedField):
    def __init__(self, model_field, **kwargs):
        # Store the field so that we can dynamically get the queryset and
        # view_name from it
        self.model_field = model_field
        self.read_only = kwargs.get('read_only', False)
        super().__init__(**kwargs)

    @property
    def queryset(self):
        if self.read_only:
            return None # So RelatedField.__init__ doesn't complain
        return self.model_field.related_model._default_manager.all()

    @queryset.setter
    def queryset(self, val):
        # we should never be assigning an actual value to this property
        assert val == None

    @property
    def view_name(self):
        return get_detail_view_name(self.model_field.related_model)

    @view_name.setter
    def view_name(self, val):
        # We should never be assigning an actual value to this property
        assert val == DUMMY_VIEW_NAME

class DynamicRelationField(HyperlinkedRelatedField):
    def __init__(self, model_field, **kwargs):
        self.model_field = model_field
        super().__init__(**kwargs)

    @property
    def view_name(self):
        return get_detail_view_name(self.model_field.related_model)

    @view_name.setter
    def view_name(self, val):
        assert val == DUMMY_VIEW_NAME

class BaseSerializer(serializers.HyperlinkedModelSerializer):
    # TODO: Describe these options
    """
    Base class used for all serializers in this project.
    """
    def __init__(self, *args, **kwargs):
        self.serializer_field_mapping[DynamicForeignKey] = DynamicForeignKeyField
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
        if not hasattr(self.Meta, 'depth'):
            self.Meta.depth = 0
        self.extra_fields = getattr(self.Meta, 'extra_fields', [])
        self.always_nest = getattr(self.Meta, 'always_nest', [])
        self.nest_if_recursive = getattr(self.Meta, 'nest_if_recursive', [])
        self.never_nest = getattr(self.Meta, 'never_nest', [])
        self.is_recursive = getattr(self.Meta, 'is_recursive', bool(self.Meta.depth))
        if self.is_recursive:
            self.always_nest = self.always_nest + self.nest_if_recursive

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
        field_names = list(field_names)
        extra_fields = getattr(self.Meta, 'extra_fields', [])
        return field_names + extra_fields

    def build_field(self, field_name, info, model_class, nested_depth):
        if field_name in self.always_nest:
            relation_info = info.relations[field_name]
            field_class, field_kwargs = self.build_nested_field(
                field_name,
                relation_info,
                max(nested_depth, 1)
            )
        elif field_name in info.fields_and_pk:
            model_field = info.fields_and_pk[field_name]
            # DynamicForeignKeys do not appear as relations in ``info`` but
            # should be treated as relations, so we have to handle them in a
            # special way
            if isinstance(model_field, DynamicForeignKey):
                field_class, field_kwargs = self.build_dynamic_foreign_key_field(
                    field_name, model_field
                )
            elif isinstance(model_field, DynamicRelation):
                field_class, field_kwargs = self.build_dynamic_relation_field(
                    field_name, model_field, nested_depth
                )
            else:
                field_class, field_kwargs = \
                        self.build_standard_field(field_name, model_field)
        elif field_name in info.relations:
            relation_info = info.relations[field_name]
            if not nested_depth:
                field_class, field_kwargs = \
                        self.build_relational_field(field_name, relation_info)
            else:
                field_class, field_kwargs = self.build_nested_field(
                    field_name, relation_info, nested_depth
                )
        elif hasattr(model_class, field_name):
            field_class, field_kwargs = \
                    self.build_property_field(field_name, model_class)
        elif field_name == api_settings.URL_FIELD_NAME:
            field_class, field_kwargs = \
                    self.build_url_field(field_name, model_class)
        else:
            field_class, field_kwargs = \
                    self.build_unknown_field(field_name, model_class)
        # Disable posting in recursive queries
        if self.is_recursive:
            field_kwargs['read_only'] = True
        return field_class, field_kwargs

    def build_dynamic_foreign_key_field(self, field_name, model_field):
        field_class = DynamicForeignKeyField
        field_kwargs = {
            'model_field': model_field,
            # The view_name has to be generated dynamically, so we provide a
            # dummy value here and throw it away later
            'view_name': DUMMY_VIEW_NAME,
        }
        return field_class, field_kwargs

    def build_dynamic_relation_field(self, field_name, model_field, nested_depth):
        if field_name in self.never_nest or nested_depth == 0:
            field_class = DynamicRelationField
            field_kwargs = {
                'model_field': model_field,
                'view_name': DUMMY_VIEW_NAME,
                'read_only': True,
                'many': True,
            }
        else:
            class NestedSerializer(BaseSerializer):
                class Meta:
                    model = model_field.related_model
                    depth = nested_depth - 1
            NestedSerializer.Meta.always_nest = self.always_nest
            NestedSerializer.Meta.never_nest = self.never_nest
            sub_extra_fields = [field for field in self.extra_fields if
                                hasattr(NestedSerializer.Meta.model, field)]
            NestedSerializer.Meta.extra_fields = sub_extra_fields
            field_class = NestedSerializer
            field_kwargs = {
                'many': True,
                'read_only': True,
            }
        return field_class, field_kwargs

    def build_nested_field(self, field_name, relation_info, nested_depth):
        if field_name in self.never_nest:
            return super().build_relational_field(field_name, relation_info)
        class NestedSerializer(BaseSerializer):
            class Meta:
                model = relation_info.related_model
                depth = nested_depth - 1
        NestedSerializer.Meta.always_nest = self.always_nest
        NestedSerializer.Meta.never_nest = self.never_nest
        sub_extra_fields = [field for field in self.extra_fields if
                            hasattr(NestedSerializer.Meta.model, field)]
        NestedSerializer.Meta.extra_fields = sub_extra_fields
        field_class = NestedSerializer
        field_kwargs = get_nested_relation_kwargs(relation_info)
        return field_class, field_kwargs
