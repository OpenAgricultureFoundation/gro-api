from django.apps import apps
from django.db import router
from django.db.models.deletion import CASCADE, SET_DEFAULT, SET_NULL
from django.db.models.fields import Field
from django.db.models.fields.related import (
    RelatedField, ForeignObject, ForeignKey, ForeignObjectRel,
    add_lazy_relation, ReverseSingleRelatedObjectDescriptor
)
from django.utils.encoding import smart_text
from django.utils.functional import cached_property, curry
from django.utils.translation import ugettext_lazy as _

from .state import StateVariable
from .errors import FarmNotConfiguredError
from farms.models import Farm

def state_dependent_attribute(state_var):
    """
    Create an attribute that stores a different value depending on some
    application state variable

    :param state_var: A :class:`cityfarm_api.state.StateVariable` instance that
        represents that application state variable on which this attribute
        depends
    """
    assert isinstance(state_var, StateVariable)
    class Class:
        def __init__(self, name):
            self.name = name

        def set_default(self, default):
            self.default = default
            return self  # To allow for chaining

        def internal_name_for_state(self, state):
            return "_{}_{}".format(state, self.name)

        @property
        def internal_name(self):
            return self.internal_name_for_state(
                state_var.current_value()
            )

        def get_for_state(self, instance, state):
            internal_name = self.internal_name_for_state(state)
            if hasattr(self, 'default'):
                return getattr(instance, internal_name, self.default)
            else:
                return getattr(instance, internal_name)

        def __get__(self, instance, instance_type=None):
            if instance is None:
                return self
            return self.get_for_state(instance, state_var.current_value())

        def set_for_state(self, instance, value, state):
            setattr(instance, self.internal_name_for_state(state), value)

        def set_for_all_states(self, instance, value):
            for state in state_var.allowed_states():
                self.set_for_state(instance, value, state)

        def __set__(self, instance, value):
            setattr(instance, self.internal_name, value)
    return Class

def state_dependent_cached_property(state_var):
    """
    Returns a decorator that converts a method with a single argument, ``self``
    into a property cached on the instance dependent on some application state
    variable.

    :param func state: A callable that returns a string representing the current
        application state on which this property depends.
    """
    assert isinstance(state_var, StateVariable)
    class Class:
        def __init__(self, func):
            self.name = func.__name__
            self.func = func
            self.__doc__ = getattr(func, '__doc__')

        def internal_name_for_state(self, state):
            return "_{}_{}".format(state, self.name)

        @property
        def internal_name(self):
            return self.internal_name_for_state(state_var.current_value())

        def get_for_state(self, instance, state):
            return instance.__dict__[internal_name_for_state(state)]

        def __get__(self, instance, instance_type=None):
            if instance is None:
                return self
            internal_name = self.internal_name
            if internal_name not in instance.__dict__:
                setattr(instance, internal_name, self.func(instance))
            return instance.__dict__[internal_name]
    return Class

def dynamic_related_field(state_var):
    """
    Returns a version of :class:`django.db.models.fields.related.RelatedField`
    that work for dynamic relations that point to different models depending on
    some application state variable.
    """
    assert isinstance(state_var, StateVariable)
    StateDependentAttribute = state_dependent_attribute(state_var)
    class Class(RelatedField):
        is_dynamic = True
        name = StateDependentAttribute('name')
        verbose_name = StateDependentAttribute('verbose_name')
        to  = StateDependentAttribute('to').set_default(None)
        def __init__(self, *args, **kwargs):
            RelatedField.__init__(self, *args, **kwargs)

        @property
        def related_model(self):
            # This property can't be cached in a dynamic field
            apps.check_models_ready()
            return self.rel.to

        def check(self):
            # We can't statically check anything in a dynamic field
            # TODO: Perform checks for all states
            pass

        def contribute_to_class(self, cls, name, virtual_only=False):
            Field.contribute_to_class(self, cls, name, virtual_only=virtual_only)
            self.opts = cls._meta
            if not cls._meta.abstract and self.rel.related_name:
                related_name = force_text(self.rel.related_name) % {
                    'class': cls.__name__.lower(),
                    'app_label': cls._meta.app_label.lower()
                }
                self.rel.related_name = related_name

        def init_for_state(self, cls, name, state, virtual_only=False):
            other = self.to_for_state(state)
            if isinstance(other, str) or other._meta.pk is None:
                # Even though we haven't resolved this reference, we have to
                # store something in `to` on initialization so Django sees that
                # this field is pointing to something and treats it as a normal
                # ForeignKey
                Class.to.set_for_state(self, other, state)
                def resolve_related_class(field, model, cls):
                    Class.to.set_for_state(self, model, state)
                    field.do_related_class(model, cls, state)
                add_lazy_relation(cls, self, other, resolve_related_class)
            else:
                self.do_related_class(model, cls, state)

        def set_attributes_from_rel(self, state):
            if Class.name.get_for_state(self, state) is None:
                to = Class.to.get_for_state(self, state)
                name = to._meta.model_name + '_' + to._meta.pk.name,
                Class.name.set_for_state(self, name, state)
            if Class.verbose_name.get_for_state(self, state) is None:
                to = Class.to.get_for_state(self, state)
                verbose_name = to._meta.verbose_name
                Class.verbose_name.set_for_state(self, verbose_name, state)
            self.rel.set_field_name()

        def do_related_class(self, other, cls, state):
            self.set_attributes_from_rel(state)
            if not cls._meta.abstract:
                self.contribute_to_related_class(other, self.rel)
    return Class

def dynamic_foreign_object_rel(state_var):
    assert isinstance(state_var, StateVariable)
    class Class(ForeignObjectRel):
        def __init__(self, field, related_name=None, limit_choices_to=None,
                parent_link=False, on_delete=None, related_query_name=None):
            self.field = field
            self.related_name = related_name
            self.related_query_name = related_query_name
            self.limit_choices_to = {} if limit_choices_to is None else \
                limit_choices_to
            self.multiple = True
            self.parent_link = parent_link
            self.on_delete = on_delete
            self.symmetrical = False

        @property
        def to(self):
            # Read this from the field because it is dynamic
            return self.field.to

        @property
        def model(self):
            # We can't cache this because to is dynamic
            return self.to

        @property
        def name(self):
            return self.field.related_query_name()
    return Class

def dynamic_many_to_one_rel(state_var):
    assert isinstance(state_var, StateVariable)
    DynamicForeignObjectRel = dynamic_foreign_object_rel(state_var)
    class Class(DynamicForeignObjectRel):
        def __init__(self, field, field_name, related_name=None,
                limit_choices_to=None, parent_link=False, on_delete=None,
                related_query_name=None):
            super().__init__(field, related_name=related_name,
                    limit_choices_to=limit_choices_to, parent_link=parent_link,
                    on_delete=on_delete, related_query_name=related_query_name)
            self.field_name = field_name

        def get_related_field(self):
            """
            Returns the Field in the 'to' object to which this relationship is
            tied
            """
            field = self.to._meta.get_field(self.field_name)
            if not field.concrete:
                raise FieldDoesNotExist("No related field named '%s'" %
                        self.field_name)
            return field

        def set_field_name(self):
            self.field_name = self.field_name or self.to._meta.pk.name
    return Class

def dynamic_reverse_single_related_object_descriptor(state_var):
    assert isinstance(state_var, StateVariable)
    class Class(ReverseSingleRelatedObjectDescriptor):
        def __init__(self, field_with_rel):
            self.field = field_with_rel
            self.cache_name_suffix = self.field.get_cache_name()

        def cache_name_for_state(self, state):
            return '_' + state + self.cache_name_suffix

        @property
        def cache_name(self):
            return self.cache_name_for_state(state_var.current_value())
    return Class

def dynamic_foreign_object(state_var):
    """
    Returns a version of :class:`django.db.models.fields.related.ForeignObject`
    that works for dynamic relations that point to different models depending on
    some application state variable.
    """
    assert isinstance(state_var, StateVariable)
    DynamicRelatedField = dynamic_related_field(state_var)
    DynamicForeignObjectRel = dynamic_foreign_object_rel(state_var)
    DynamicReverseSingleRelatedObjectDescriptor = \
        dynamic_reverse_single_related_object_descriptor(state_var)
    class Class(DynamicRelatedField, ForeignObject):
        def __init__(self, from_fields, to_fields, swappable=True, **kwargs):
            self.from_fields = from_fields
            self.to_fields = to_fields = to_fields
            self.swappable = swappable

            if not 'rel' in kwargs:
                kwargs['rel'] = DynamicForeignObjectRel(
                    self, related_name=kwargs.pop('related_name', None),
                    related_query_name=kwargs.pop('related_query_name', None),
                    limit_choices_to=kwargs.pop('limit_choices_to', None),
                    parent_link=kwargs.pop('parent_link', False),
                    on_delete=kwargs.pop('on_delete', CASCADE),
                )
            kwargs['verbose_name'] = kwargs.get('verbose_name', None)

            DynamicRelatedField.__init__(self, **kwargs)

        def check(self):
            # We can't statically check anything in a dynamic field
            return []

        def deconstruct(self):
            name, path, args, kwargs = DynamicRelatedField.deconstruct(self)
            kwargs['from_fields'] = self.from_fields
            kwargs['to_fields'] = self.to_fields
            if self.rel.related_name is not None:
                kwargs['related_name'] = self.rel.related_name
            if self.rel.related_query_name is not None:
                kwargs['related_query_name'] = self.rel.related_query_name
            if self.rel.on_delete != CASCADE:
                kwargs['on_delete'] = self.rel.on_delete
            if self.rel.parent_link:
                kwargs['parent_link'] = self.rel.parent_link
            # I don't think we can do anything with to or swappable_setting
            return name, path, args, kwargs

        def contribute_to_class(self, cls, name, virtual_only=False):
            DynamicRelatedField.contribute_to_class(
                self, cls, name, virtual_only=virtual_only
            )
            setattr(cls, self.name, DynamicReverseSingleRelatedObjectDescriptor(self))

        def contribute_to_related_class(self, cls, related):
            if not related.hidden and not related.related_model._meta.swapped:
                # This has to be idempotent because it can be called once per
                # state
                if not hasattr(cls, related.get_accessor_name()):
                    setattr(
                        cls, related.get_accessor_name(),
                        self.related_accessor_class(related)
                    )
                if related.limit_choices_to:
                    cls._meta.related_fkey_lookups.append(related.limit_choices_to)
    return Class

def dynamic_foreign_key(state_var):
    """
    Returns a version of :class:`django.db.models.fields.related.ForeignKey`
    that works for dynamic relations that point to different models depending on
    some application state variable.
    """
    assert isinstance(state_var, StateVariable)
    DynamicForeignObject = dynamic_foreign_object(state_var)
    DynamicManyToOneRel = dynamic_many_to_one_rel(state_var)
    class Class(DynamicForeignObject, ForeignKey):
        empty_strings_allowed = False
        default_error_messages = {
            'invalid': _('%(model)s instance with %(field)s %(value)r does not '
                'exist')
        }
        description = _('Foreign Key (type determined by related field)')
        def __init__(self, to_field=None, rel_class=DynamicManyToOneRel,
                db_constraint=True, **kwargs):
            if to_field:
                self.to_field = to_field
            if 'db_index' not in kwargs:
                kwargs['db_index'] = True
            self.db_constraint = db_constraint
            kwargs['rel'] = rel_class(
                self, to_field, related_name=kwargs.pop('related_name', None),
                related_query_name=kwargs.pop('related_query_name', None),
                limit_choices_to=kwargs.pop('limit_choices_to', None),
                parent_link=kwargs.pop('parent_link', False),
                on_delete=kwargs.pop('on_delete', CASCADE),
            )
            DynamicForeignObject.__init__(self, ['self'], [to_field], **kwargs)

        @state_dependent_cached_property(state_var)
        def to_field(self):
            # Assumes that all possible values of to for all states have the
            # same pk field.
            # TODO: Implement this as a check
            return self.to._meta.pk and self.to._meta.pk.name
        def check(self, **kwargs):
            errors = DynamicForeignObject.check(self, **kwargs)
            errors.extend(self._check_on_delete())
            errors.extend(self._check_unique())
            return errors
        def deconstruct(self):
            name, path, args, kwargs = DynamicForeignObject.deconstruct(self)
            del kwargs['to_fields']
            del kwargs['from_fields']
            if self.db_index:
                del kwargs['db_index']
            else:
                kwargs['db_index'] = False
            if self.db_constraint is not True:
                kwargs['db_constraint'] = self.db_constraint
            to_meta = None
            try:
                to_meta = self.rel.to._meta
            except AttributeError:
                pass
            if self.rel.field_name and (not to_meta or (to_meta.pk and self.rel.field_name != to_meta.pk.name)):
                kwargs['to_field'] = self.rel.field_name
            return name, path, args, kwargs
    return Class
