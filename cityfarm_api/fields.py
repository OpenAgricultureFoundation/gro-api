"""
This module defines a set of functions necessary to produce modified ForeignKey
fields that change their behavior based on some application-level state
variable.
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

        def internal_name_for_state(self, state):
            """
            The name of the attribute on the parent instance in which to store
            the value of this attribute for the given state

            :param str state: The state for which to get the internal name
            """
            return "_{}_{}".format(state, self.name)

        @property
        def internal_name(self):
            """
            The internal name for the current state (see
            :func:`internal_name_for_state`).
            """
            return self.internal_name_for_state(
                state_var.current_value()
            )

        def get_for_state(self, instance, state):
            """
            Get the value of this attribute for the given instance and state

            :param instance: The object for which this attribute is being read
            :param str state: The state for which to get this attribute value
            """
            internal_name = self.internal_name_for_state(state)
            return getattr(instance, internal_name)

        def __get__(self, instance, instance_type=None):
            if instance is None:
                return self
            return self.get_for_state(instance, state_var.current_value())

        def set_for_state(self, instance, value, state):
            """
            Set the value of this attribute for the given instance and state

            :param instance: The object for which this attribute is being set
            :param value: The value to save
            :param str state: The state for which to set this attribute value
            """
            setattr(instance, self.internal_name_for_state(state), value)

        def set_for_all_states(self, instance, value):
            """
            Set a value for this attributes for all possible states

            :param instance: The object for which this attribute is being set
            :param value: The value to save
            """
            for state in state_var.allowed_values():
                self.set_for_state(instance, value, state)

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

        def internal_name_for_state(self, state):
            """
            The name of the attribute on the parent instance in which to store
            the value of this property for the given state

            :param str state: The state for which to get the internal name
            """
            return "_{}_{}".format(state, self.name)

        @property
        def internal_name(self):
            """
            The internal name for the current state (see
            :func:`internal_name_for_state`)
            """
            return self.internal_name_for_state(state_var.current_value())

        def get_for_state(self, instance, state):
            """
            Get the value of this attribute for the given instance and state

            :param instance: The object for which this property is being read
            :param str state: The state for which to get this property value
            """
            return instance.__dict__[self.internal_name_for_state(state)]

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
    Returns a :class:`django.db.models.fields.related.RelatedField` subclass
    that works for dynamic relations that point to different models depending on
    some application state variable. The `to` attribute of the returned class
    will be a :func:`state_dependent_attribute` that depends on the given state
    variable.

    Subclasses of the returned class must define a method :meth:`to_for_state`
    that takes a single argument `state` and returns the name of the model that
    this field points to for the state given by the `state` argument. They must
    also define a method `contribute_to_related_class` that takes 2 arguments,
    `cls` (the other class to contribute to) and `related` (the rel object
    describing the relation to the other class).

    :param state_var: A :class:`~cityfarm_api.state.StateVariable` instance that
        represents the application state variable on which the behavior of the
        returned field depends.
    """
    assert isinstance(state_var, StateVariable)
    StateDependentAttribute = state_dependent_attribute(state_var)
    class Class(RelatedField):
        """ The dynamic RelatedField class to return """
        # It is useful to have some indicator that this field is dynamic.  We
        # can't always tell by simple type inspection because this class is
        # generated dynamically and most scopes won't have access to it.
        is_dynamic = True
        to = StateDependentAttribute('to')
        name = StateDependentAttribute('name')
        verbose_name = StateDependentAttribute('verbose_name')
        def __init__(self, *args, **kwargs):
            # Django requires a value `to` attribute to be set on the field upon
            # initialization because some of the migration logic constructs the
            # field without installing it in a model and then checks the
            # `rel.to` attribute to figure out things about this field. Django
            # also assumes that the deconstruction of a RelatedField will have a
            # value for `to` in it's deconstruction, so we save the actual value
            # in :meth:`deconstruct` just to be safe and ignore it here. We will
            # set and actually resolve the attribute in :meth:`set_for_state`.
            kwargs.pop('to', None)
            self.to = self.to_for_state(state_var.current_value())
            RelatedField.__init__(self, *args, **kwargs)

        def to_for_state(self, state):
            """
            Returns the name of the model that this field points to for the
            given state. Subclasses of this class must implement
            :meth:`to_for_state`.

            :param: The application state to inspect.
            """
            raise NotImplementedError()

        @property
        def related_model(self):
            # This property can't be cached in a dynamic field
            apps.check_models_ready()
            return self.to

        def __check_relation_model_exists(self, state):
            """
            Performs the RelatedField._check_relation_model_exists check for the
            application state given by `state`.
            """
            to = Class.to.get_for_state(self, state)
            rel_is_missing = to not in apps.get_models()
            rel_is_string = isinstance(to, str)
            model_name = to if rel_is_string else to._meta.object_name
            if rel_is_missing and (rel_is_string or not to._meta.swapped):
                return [
                    checks.Error(
                        ("For state '%s', field defines a relation with model "
                         "'%s', which is either not installed, or is abstract.")
                        % (state, model_name),
                        hint=None,
                        obj=self,
                        id='fields.E300',
                    )
                ]
            return []

        def _check_relation_model_exists(self):
            errors = []
            for state in state_var.allowed_values():
                errors.extend(self.__check_relation_model_exists(state))
            return errors

        def __check_referencing_to_swapped_model(self, state):
            """
            Performs the RelatedField._check_referencing_to_swapped_model check
            for the application state given by `state`
            """
            to = Class.to.get_for_state(self, state)
            if (to not in apps.get_models() and not isinstance(to, str) and
                    to._meta.swapped):
                model = "%s.%s" % (to._meta.app_label, to._meta.object_name)
                return [
                    checks.Error(
                        ("For state '%s', field defines a relation with the "
                         "model '%s', which has been swapped out.") %
                        (state, model),
                        hint="Update the relation to point at 'settings.%s'." %
                        to._meta.swappable,
                        obj=self,
                        id='fields.E301',
                    )
                ]
            return []

        def _check_referencing_to_swapped_model(self):
            errors = []
            for state in state_var.allowed_values():
                errors.extend(self.__check_referencing_to_swapped_model(state))
            return errors

        def __check_clashes(self, state):
            """
            Performs the RelatedField._check_clashes check for the application
            state given by `state`
            """
            # This is almost identical to RelatedField._check_clashes except
            # that we have to pull the `to` value for the specified state
            errors = []
            opts = self.model._meta
            to = Class.to.get_for_state(self, state)
            if isinstance(to, str):
                # To hasn't been resolved yet, so we can't really check it
                return []
            if self.rel.is_hidden():
                # f the field doesn't install a backward relation on the target
                # model, then there are no clashes to check for
                return []

            rel_opts = to._meta
            rel_name = self.rel.get_accessor_name()
            rel_query_name = self.related_query_name()
            field_name = "%s.%s" % (opts.object_name, self.name)

            potential_clashes = rel_opts.fields + rel_opts.many_to_many
            for clash_field in potential_clashes:
                clash_name = "%s.%s" % (rel_opts.object_name, clash_field.name)
                if clash_field.name == rel_name:
                    errors.append(
                        checks.Error(
                            ("Reverse acessor for '%s' clashes with field name "
                             "'%s'.") % (field_name, clash_name),
                            hint=
                            ("Rename field '%s', or add/change a related_name "
                             "argument to the definition for field '%s'") %
                            (clash_name, field_name),
                            obj=self,
                            id='fields.E302',
                        )
                    )
                if clash_field.name == rel_query_name:
                    errors.append(
                        checks.Error(
                            ("Reverse query name for '%s' clashes with field "
                             "name '%s'.") % (field_name, clash_name),
                            hint=
                            ("Rename field '%s', or add/change a related_name "
                             "argument to the definition for field '%s'.") %
                            (clash_name, field_name),
                            obj=self,
                            id='fields.E303',
                        )
                    )

            potential_clashes = (
                r for r in rel_opts.related_objects if r.field is not self
            )
            for clash_field in potential_clashes:
                clash_name = '%s.%s' % (
                    clash_field.related_model._meta.object_name,
                    clash_field.field.name
                )
                if clash_field.get_accessor_name() == rel_name:
                    errors.append(
                        checks.Error(
                            ("Reverse accessor for '%s' clashed with reverse "
                             "accessor for '%s'.") % (field_name, clash_name),
                            hint=
                            ("Add or change a related_name argument to the "
                             "definition for '%s' or '%s'.") %
                            (field_name, clash_name),
                            obj=self,
                            id='fields.E304',
                        )
                    )
                if clash_field.get_accessor_name() == rel_query_name:
                    errors.append(
                        checks.Error(
                            ("Reverse query name for '%s' clashed with reverse "
                             "query name for '%s'.") % (field_name, clash_name),
                            hint=
                            ("Add or change a related_name argument to the "
                             "definition for '%s' or '%s'.") %
                            (field_name, clash_name),
                            obj=self,
                            id='fields.E305',
                        )
                    )
            return errors

        def _check_clashes(self):
            errors = []
            for state in state_var.allowed_values():
                errors.extend(self.__check_clashes(state))
            return errors

        def deconstruct(self):
            name, path, args, kwargs = RelatedField.deconstruct(self)
            if isinstance(self.to, str):
                kwargs['to'] = self.to
            else:
                kwargs['to'] = '%s.%s' % (
                    self.to._meta.app_label, self.to._meta.object_name
                )
            return name, path, args, kwargs

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
            # We already have something stored in `to` for the current state
            # from __init__ but we're going to overwrite it anyway and resolve
            # `to` for all states now that we know models are being loaded
            for state in state_var.allowed_values():
                other = self.to_for_state(state)
                if isinstance(other, str) or other._meta.pk is None:
                    def resolve_related_class(field, model, cls, state=state):
                        Class.to.set_for_state(self, model, state)
                        field.do_related_class_for_state(model, cls, state)
                    add_lazy_relation(cls, self, other, resolve_related_class)
                else:
                    self.do_related_class(other, cls, state)

        def contribute_to_related_class(self, cls, related):
            """
            Subclasses of this class must implement
            `contribute_to_related_class`
            """
            raise NotImplementedError()

        def set_attributes_from_rel(self):
            raise Exception(
                'This function should never be called. Use '
                '`set_attributes_from_rel_for_state` instead'
            )

        def set_attributes_from_rel_for_state(self, state):
            """
            Perform the function of `set_attributes_from_rel` for the
            application state given by `state`.
            """
            to = Class.to.get_for_state(self, state)
            name = Class.name.get_for_state(self, state)
            if name is None:
                name = to._meta.model_name + '_' + to._meta.pk.name,
                Class.name.set_for_state(self, name, state)
            verbose_name = Class.verbose_name.get_for_state(self, state)
            if verbose_name is None:
                verbose_name = to._meta.verbose_name
                Class.verbose_name.set_for_state(self, verbose_name, state)
            self.rel.set_field_name_for_state(state)

        def do_related_class(self, other, cls):
            raise Exception(
                'This function should never be called. Use '
                '`do_related_class_for_state` instead'
            )

        def do_related_class_for_state(self, other, cls, state):
            """
            Perform the function of `do_related_class` for the application state
            given by `state`.
            """
            self.set_attributes_from_rel(state)
            if not cls._meta.abstract:
                self.contribute_to_related_class(other, self.rel)
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
            Class.field_name.set_for_all_states(self, field_name)

        def set_field_name(self):
            """
            :meth:`set_field_name_for_state` should be used instead of this
            """
            raise NotImplementedError()

        def set_field_name_for_state(self, state):
            """
            Perform the same function as the old :meth:`set_field_name` but only
            for the state given by `state`.
            """
            field_name = Class.field_name.get_for_state(self, state) or \
                self.to._meta.pk.name
            Class.field_name.set_for_state(self, field_name, state)
    return Class

def dynamic_foreign_object(state_var):
    """
    Returns a version of :class:`django.db.models.fields.related.ForeignObject`
    that works for dynamic relations that point to different models depending on
    some application state variable. The main difference between this and
    `ForeignObject` is that the constructor for this class does not accept the
    `to` attribute, because that is provided dynamically.

    Subclasses of the returned class must define a method :meth:`to_for_state`
    that takes a single argument `state` and returns the name of the model that
    this field points to for the state given by the `state` argument.

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

        def to_for_state(self, state):
            raise NotImplementedError()

        def check(self, **kwargs):
            errors = DynamicRelatedField.check(self, **kwargs)
            errors.extend(self._check_unique_target())
            return errors

        def __check_unique_target(self, state):
            """
            Performs the ForeignObject._check_unique_target check for the
            application state given by `state`.
            """
            to = Class.to.get_for_state(self, state)
            rel_is_string = isinstance(to, str)
            if rel_is_string or not self.requires_unique_target:
                return []
            try:
                self.foreign_related_fields
            except FieldDoesNotExist:
                return []
            has_unique_field = any(
                rel_field.unique for rel_field in self.foreign_related_fields
            )
            if not has_unique_field and len(self.foreign_related_fields) > 1:
                field_combination = ', '.join(
                    "'%s'" % rel_field.name for rel_field in
                    self.foreign_related_fields
                )
                model_name = to.__name__
                return [
                    checks.Error(
                        ("None of the fields %s on model '%s' have a unique=True"
                         " constraint.") % (field_combination, model_name),
                        hint=None,
                        obj=self,
                        id='fields.E310',
                    )
                ]
            elif not has_unique_field:
                field_name = self.foreign_related_fields[0].name
                model_name = to.__name__
                return [
                    checks.Error(
                        ("'%s.%s' must set unique=True because it is "
                         "references by a foreign key.") %
                        (model_name, field_name),
                        hint=None,
                        obj=self,
                        id='fields.E311',
                    )
                ]
            else:
                return []

        def _check_unique_target(self):
            errors = []
            for state in state_var.allowed_values():
                errors.extend(self.__check_unique_target(state))
            return errors

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

    Subclasses of the returned class must define a method :meth:`to_for_state`
    that takes a single argument `state` and returns the name of the model that
    this field points to for the state given by the `state` argument.

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

        def to_for_state(self, state):
            raise NotImplementedError()

        @cached_property
        def to_field(self): # pylint: disable=method-hidden
            """
            If :attr:`to_field` is not set in init, generate it and indicate to
            :meth:`_check_consistent_to_field` that it doesn't need to perform
            it's check.
            """
            self.generated_to_field = True
            return self.to._meta.pk and self.to._meta.pk.name

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
                for state in state_var.allowed_values():
                    to = Class.to.get_for_state(self, state)
                    if not (to._meta.pk and to._meta.pk.name) == self.to_field:
                        model_name = to._meta.object_name
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
            if self.rel.field_name and (not to_meta or \
                    (to_meta.pk and self.rel.field_name != to_meta.pk.name)):
                kwargs['to_field'] = self.rel.field_name
            return name, path, args, kwargs

        def contribute_to_related_class(self, cls, related):
            if self.rel.field_name is None:
                self.rel.field_name = cls._meta.pk.name
    return Class
