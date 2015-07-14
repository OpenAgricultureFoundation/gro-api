"""
This module defines a set of functions necessary to produce modified ForeignKey
fields that change their behavior based on some application-level state
variable. These fields are not safe for use in models that will undergo
migrations.
"""

from django.apps import apps
from django.core import checks
from django.core.exceptions import FieldDoesNotExist
from django.db.models import CASCADE
from django.db.models.fields import Field
from django.db.models.fields.related import (
    RelatedField, ForeignObject, ForeignKey, ForeignObjectRel,
    add_lazy_relation, ReverseSingleRelatedObjectDescriptor
)
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from .state import StateVariable

def state_dependent_attribute(state_var):
    """
    Create an attribute that stores a different value depending on some
    application state variable.

    :param state_var: A :class:`~cityfarm_api.state.StateVariable` instance that
        represents that application state variable on which this attribute
        depends
    """
    assert isinstance(state_var, StateVariable)
    class Class:
        """ The state-dependent attribute to return """
        def __init__(self, name):
            self.name = name

        @property
        def internal_name(self):
            return "_{}_{}".format(state_var.current_value, self.name)

        def __get__(self, instance, instance_type=None):
            if instance is None:
                return self
            return getattr(instance, self.internal_name)

        def __set__(self, instance, value):
            setattr(instance, self.internal_name, value)
    return Class

def state_dependent_cached_property(state_var):
    """
    Returns a decorator that converts a method with a single argument, ``self``
    into a property cached on the instance dependent on some application state
    variable.

    :param state_var: A :class:`~cityfarm_api.state.StateVariable` instance that
        represents the application state variable on which this property
        depends
    """
    assert isinstance(state_var, StateVariable)
    class Class:
        """ The state-dependent property decorator to return """
        def __init__(self, func):
            self.name = func.__name__
            self.func = func
            self.__doc__ = getattr(func, '__doc__')

        @property
        def internal_name(self):
            return "_{}_{}".format(state_var.current_value, self.name)

        def __get__(self, instance, instance_type=None):
            if instance is None:
                return self
            if not hasattr(instance, self.internal_name):
                setattr(instance, self.internal_name, self.func(instance))
            return getattr(instance, self.internal_name)
    return Class

def dynamic_related_field(state_var):
    """
    Returns a :class:`django.db.models.fields.related.RelatedField` subclass
    that works for dynamic relations that point to different models depending on
    some application state variable. The `to` attribute of the returned class
    will be a :func:`state_dependent_attribute` that depends on the given state
    variable.

    Subclasses of the returned class must define a method
    :meth:`get_other_model` that returns the name of the model that this field
    points to for the current state.  They must also define a method
    `contribute_to_related_class` that takes 2 arguments, `cls` (the other class
    to contribute to) and `related` (the rel object describing the relation to
    the other class).

    :param state_var: A :class:`~cityfarm_api.state.StateVariable` instance that
        represents the application state variable on which the behavior of the
        returned field depends.
    """
    assert isinstance(state_var, StateVariable)
    StateDependentAttribute = state_dependent_attribute(state_var)
    StateDependentCachedProperty = state_dependent_cached_property(state_var)
    class Class(RelatedField):
        """ The dynamic RelatedField class to return """
        # It is useful to have some indicator that this field is dynamic.  We
        # can't always tell by simple type inspection because this class is
        # generated dynamically and most scopes won't have access to it.
        is_dynamic = True
        to = StateDependentAttribute('to')

        def __init__(self, *args, **kwargs):
            for state in state_var.allowed_values:
                with state_var.as_value(state):
                    self.to = self.get_other_model()
            Field.__init__(self, *args, **kwargs)

        def get_other_model(self, state):
            """
            Returns the name of the model that this field points to for the
            given state. Subclasses of this class must implement
            :meth:`get_other_model`.

            :param: The application state to inspect.
            """
            raise NotImplementedError()

        @property
        def related_model(self):
            # This property can't be cached in a dynamic field
            apps.check_models_ready()
            return self.to

        def check(self, **kwargs):
            errors = Field.check(self, **kwargs)
            errors.extend(self._check_related_name_is_valid())
            for state in state_var.allowed_values:
                with state_var.as_value(state):
                    if self.to is None:
                        # This should only happen if `cls` is not going to be
                        # used for `state`. Thus, we shouldn't have to check
                        # this
                        continue
                    state_errors = []
                    state_errors.extend(self._check_relation_model_exists())
                    state_errors.extend(self._check_referencing_to_swapped_model())
                    state_errors.extend(self._check_clashes())
                    for err in state_errors:
                        err.msg = 'With state {}: '.format(state) + err.msg
                    errors.extend(state_errors)
            return errors

        def deconstruct(self):
            raise NotImplementedError()

        def contribute_to_class(self, cls, name, virtual_only=False):
            # We need to skip RelatedField in the mro, so we can't use `super()`
            Field.contribute_to_class(
                self, cls, name, virtual_only=virtual_only
            )
            self.opts = cls._meta
            if not cls._meta.abstract and self.rel.related_name:
                related_name = force_text(self.rel.related_name) % {
                    'class': cls.__name__.lower(),
                    'app_label': cls._meta.app_label.lower()
                }
                self.rel.related_name = related_name
            for state in state_var.allowed_values:
                with state_var.as_value(state):
                    other = self.to
                    if other is None:
                        # This should only happen if `cls` is not going to be
                        # used for `state`. Just leave the null value there
                        continue
                    if isinstance(other, str) or other._meta.pk is None:
                        def resolve_related_class(
                            field, model, cls, state=state_var.current_value
                        ):
                            with state_var.as_value(state):
                                field.to = model
                                field.do_related_class(model, cls)
                        add_lazy_relation(
                            cls, self, other, resolve_related_class
                        )
                    else:
                        self.do_related_class(other, cls)

        def contribute_to_related_class(self, cls, related):
            """
            Subclasses of this class must implement
            `contribute_to_related_class`
            """
            raise NotImplementedError()
    return Class

def dynamic_foreign_object_rel(state_var):
    """
    Returns a :class:`~django.db.models.fields.related.ForeignObjectRel`
    subclass that understands that it's related field will be dynamic and that
    it can't cache certain things about the model being referenced by this
    relation. The main difference between the returned class and
    ForeignObjectRel externally is that it's constructor doesn't take a `to`
    argument, as the relation just reads from the `to` attribute of the related
    field.

    :param state_var: A class :class:`cityfarm_api.state.StateVairable` instance
        that represents the application state variable on which the behavior of
        this relation depends.
    """
    assert isinstance(state_var, StateVariable)
    class Class(ForeignObjectRel):
        """ The dynamic ForeignObjectRel class to return """
        def __init__(self, field, related_name=None, limit_choices_to=None, \
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
            """ Read `to` from the field because it is dynamic """
            return self.field.to

        @property
        def model(self):
            """ We can't cache this because `to` is dynamic """
            return self.to
    return Class

def dynamic_many_to_one_rel(state_var):
    """
    Returns a version of :class:`~django.db.models.fields.related.ManyToOneRel`
    that uses the result of :func:`dynamic_foreign_object_rel` as a base instead
    of :class:`~django.db.models.fields.related.ForeignObjectRel`.

    :param state_var: A class :class:`cityfarm_api.state.StateVairable` instance
        that represents the application state variable on which the behavior of
        this relation depends.
    """
    assert isinstance(state_var, StateVariable)
    DynamicForeignObjectRel = dynamic_foreign_object_rel(state_var)
    StateDependentAttribute = state_dependent_attribute(state_var)
    class Class(DynamicForeignObjectRel):
        """ The dynamic ManyToOneRel class to return """
        field_name = StateDependentAttribute('field_name')
        def __init__(self, field, field_name, related_name=None, \
                limit_choices_to=None, parent_link=False, on_delete=None, \
                related_query_name=None):
            super().__init__(
                field, related_name=related_name,
                limit_choices_to=limit_choices_to, parent_link=parent_link,
                on_delete=on_delete, related_query_name=related_query_name
            )
            for state in state_var.allowed_values:
                with state_var.as_value(state):
                    self.field_name = field_name
    return Class

def dynamic_foreign_object(state_var):
    """
    Returns a version of :class:`django.db.models.fields.related.ForeignObject`
    that works for dynamic relations that point to different models depending on
    some application state variable. The main difference between this and
    `ForeignObject` is that the constructor for this class does not accept the
    `to` attribute, because that is provided dynamically.

    Subclasses of the returned class must define a method
    :meth:`get_other_model` that returns the name of the model that this field
    points to for the current state.

    :param state_var: A :class:`cityfarm_api.state.StateVariable` instance that
        represents the application state variable on which the behavior of the
        returned field depends.
    """
    assert isinstance(state_var, StateVariable)
    DynamicRelatedField = dynamic_related_field(state_var)
    DynamicForeignObjectRel = dynamic_foreign_object_rel(state_var)
    StateDependentAttribute = state_dependent_attribute(state_var)
    class Class(ForeignObject, DynamicRelatedField):
        """ Dynamic ForeignObject class to return """
        _related_fields = StateDependentAttribute('related_fields')
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

        def get_other_model(self, state):
            raise NotImplementedError()

        def check(self, **kwargs):
            errors = DynamicRelatedField.check(self, **kwargs)
            for state in state_var.allowed_values:
                with state_var.as_value(state):
                    if self.to is None:
                        # This should only happen if `cls` is not going to be
                        # used for `state`. Thus, we shouldn't have to check
                        # this
                        continue
                    state_errors = self._check_unique_target()
                    for err in state_errors:
                        err.msg = 'With state {}: '.format(state) + err.msg
                    errors.extend(state_errors)
            return errors

        def deconstruct(self):
            raise NotImplementedError()

        def contribute_to_class(self, cls, name, virtual_only=False):
            # We need to skip RelatedField in the mro, so we can't use `super()`
            # here
            DynamicRelatedField.contribute_to_class(
                self, cls, name, virtual_only=virtual_only
            )
            setattr(cls, self.name, ReverseSingleRelatedObjectDescriptor(self))

        def contribute_to_related_class(self, cls, related):
            if not related.hidden and not related.related_model._meta.swapped:
                # This has to be idempotent so that  it can be called once per
                # state
                if not hasattr(cls, related.get_accessor_name()):
                    setattr(
                        cls, related.get_accessor_name(),
                        self.related_accessor_class(related)
                    )
                if related.limit_choices_to:
                    cls._meta.related_fkey_lookups.append(
                        related.limit_choices_to
                    )
    return Class

def dynamic_foreign_key(state_var):
    """
    Returns a version of :class:`django.db.models.fields.related.ForeignKey`
    that works for dynamic relations that point to different models depending on
    some application state variable. The main difference between this class and
    `ForeignKey` is that the constructor does not accept the `to` attribute

    Subclasses of the returned class must define a method
    :meth:`get_other_model` that returns the name of the model that this field
    points to for the current state.

    :param state_var: A :class:`cityfarm_api.state.StateVariable` instance that
        represents the application state variable on which the behavior of the
        returned field depends
    """
    assert isinstance(state_var, StateVariable)
    DynamicForeignObject = dynamic_foreign_object(state_var)
    DynamicManyToOneRel = dynamic_many_to_one_rel(state_var)
    class Class(DynamicForeignObject, ForeignKey):
        """ The dynamic ForeignKey class to return """
        empty_strings_allowed = False
        default_error_messages = {
            'invalid': _(
                '%(model)s instance with %(field)s %(value)r does not exist'
            )
        }
        description = _('Foreign Key (type determined by related field)')
        def __init__(self, to_field=None, rel_class=DynamicManyToOneRel, \
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

        def get_other_model(self):
            raise NotImplementedError()

        @cached_property
        def to_field(self): # pylint: disable=method-hidden
            """
            If :attr:`to_field` is not set in init, generate it and indicate to
            :meth:`_check_consistent_to_field` that it doesn't need to perform
            it's check.
            """
            self.generated_to_field = True
            return self.to and self.to._meta.pk and self.to._meta.pk.name

        def check(self, **kwargs):
            errors = DynamicForeignObject.check(self, **kwargs)
            errors.extend(self._check_on_delete())
            errors.extend(self._check_unique())
            errors.extend(self._check_consistent_to_field())
            return errors

        def _check_consistent_to_field(self):
            """
            If the attribute :attr:`to_field` was generated from the name of the
            primary key of the `to` model, make sure that every model that this
            field can point to has the same primary key name.
            """
            # Make sure the `to_field` has been generated if it is going to be
            getattr(self, 'to_field')
            if 'generated_to_field' in self.__dict__ and self.generated_to_field:
                for state in state_var.allowed_values:
                    with state_var.as_value(state):
                        if self.to is not None and (self.to._meta.pk and
                                self.to._meta.pk.name) != self.to_field:
                            model_name = self.to._meta.object_name
                            return [
                                checks.Error(
                                    "DynamicForeignKey on model '%s' should point "
                                    "to a different field in the target model "
                                    "depending on the current state. This is "
                                    "currently not supported." % model_name,
                                    hint=None,
                                    obj=self,
                                    id='fields.E312',
                                )
                            ]
            return []

        def deconstruct(self):
            raise NotImplementedError()

        def contribute_to_related_class(self, cls, related):
            DynamicForeignObject.contribute_to_related_class(self, cls, related)
            if self.rel.field_name is None:
                self.rel.field_name = cls._meta.pk.name
    return Class
