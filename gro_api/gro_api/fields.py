"""
This module subclasses several of the classes in the MRO of
:class:`django.db.models.fields.related.ForeignKey` to produce a
:class:`LayoutForeignKey` field which can point to a different model depending
on the layout of the current farm.
"""

from django.core import checks
from django.db.models import CASCADE
from django.db.models.fields import Field
from django.db.models.fields.related import (
    RelatedField, ForeignObject, ForeignKey, ForeignObjectRel,
    add_lazy_relation, ForeignRelatedObjectsDescriptor,
    ReverseSingleRelatedObjectDescriptor
)
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from .utils import (
    system_layout, LayoutDependentAttribute, LayoutDependentCachedProperty
)

class LayoutRelatedField(RelatedField):
    """
    A :class:`django.db.models.fields.related.RelatedField` subclass that works
    for dynamic relations that point to different models depending on the
    layout of the current farm
    """
    # It is useful to have some indicator that this field is dynamic
    is_dynamic = True
    to = LayoutDependentAttribute('to', default=None)

    def __init__(self, *args, **kwargs):
        for state in system_layout.allowed_values:
            with system_layout.as_value(state):
                self.to = self.get_other_model()
        super().__init__(*args, **kwargs)

    def get_other_model(self):
        """
        Returns the name of the model that this field points to. Subclasses of
        :class:`LayoutRelatedField` must implement this method.
        """
        raise NotImplementedError()

    @property
    def related_model(self):
        # This property can't be cached in a dynamic field
        return self.to

    def check(self, **kwargs):
        errors = Field.check(self, **kwargs)
        errors.extend(self._check_related_name_is_valid())
        for state in system_layout.allowed_values:
            with system_layout.as_value(state):
                if self.to is None:
                    # This should only happen if `cls` is not going to be used
                    # for `state`. Thus, we can skip all of these checks
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
        for state in system_layout.allowed_values:
            with system_layout.as_value(state):
                other = self.to
                if other is None:
                    # This should only happen if `cls` is not going to be
                    # used for `state`. Just leave the null value there
                    continue
                if isinstance(other, str) or other._meta.pk is None:
                    def resolve_related_class(field, model, cls, state=state):
                        with system_layout.as_value(state):
                            field.to = model
                            field.do_related_class(model, cls)
                    add_lazy_relation(cls, self, other, resolve_related_class)
                else:
                    self.do_related_class(other, cls)

    def contribute_to_related_class(self, cls, related):
        """
        Subclasses of class:`LayoutRelatedfield` must implement this method.
        """
        raise NotImplementedError()

class LayoutForeignObjectRel(ForeignObjectRel):
    """
    Returns a :class:`~django.db.models.fields.related.ForeignObjectRel`
    subclass that understands that it's related field will be dynamic and that
    it can't cache certain things about the model being referenced by this
    relation. The main difference between the returned class and
    ForeignObjectRel externally is that it's constructor doesn't take a `to`
    argument, as the relation just reads from the `to` attribute of the related
    field.
    """
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
        return self.field.to

class LayoutManyToOneRel(LayoutForeignObjectRel):
    """
    Returns a version of :class:`~django.db.models.fields.related.ManyToOneRel`
    that uses the result of :class:`LayoutForeignObjectRel` as a base instead
    of :class:`~django.db.models.fields.related.ForeignObjectRel`.
    """
    field_name = LayoutDependentAttribute('field_name', default=None)
    def __init__(self, field, field_name, related_name=None, \
            limit_choices_to=None, parent_link=False, on_delete=None, \
            related_query_name=None):
        super().__init__(
            field, related_name=related_name,
            limit_choices_to=limit_choices_to, parent_link=parent_link,
            on_delete=on_delete, related_query_name=related_query_name
        )
        for state in system_layout.allowed_values:
            with system_layout.as_value(state):
                self.field_name = field_name

class LayoutForeignRelatedObjectsDescriptor(ForeignRelatedObjectsDescriptor):
    """
    We can't pass the related class to this descriptor on initialization
    because it varies by layout, so we make the various forward fields set the
    related attribute of this object in their
    :meth:`contribute_to_related_class` methods.
    """
    related = LayoutDependentAttribute('related')
    def __init__(self):
        pass

    @LayoutDependentCachedProperty
    def related_manager_cls(self):
        return ForeignRelatedObjectsDescriptor.related_manager_cls.func(self)

class LayoutForeignObject(ForeignObject, LayoutRelatedField):
    """
    A version of :class:`django.db.models.fields.related.ForeignObject` that
    works for dynamic relations that point to different models depending on
    the layout of the current farm. The main difference between this and
    `ForeignObject` is that the constructor for this class does not accept the
    `to` attribute, because that is provided dynamically.
    """
    _related_fields = LayoutDependentAttribute(
        'related_fields', default=None
    )
    related_accessor_class = LayoutForeignRelatedObjectsDescriptor

    def __init__(self, from_fields, to_fields, swappable=True, **kwargs):
        self.from_fields = from_fields
        self.to_fields = to_fields = to_fields
        self.swappable = swappable

        if 'rel' not in kwargs:
            kwargs['rel'] = LayoutForeignObjectRel(
                self, related_name=kwargs.pop('related_name', None),
                related_query_name=kwargs.pop('related_query_name', None),
                limit_choices_to=kwargs.pop('limit_choices_to', None),
                parent_link=kwargs.pop('parent_link', False),
                on_delete=kwargs.pop('on_delete', CASCADE),
            )
        kwargs['verbose_name'] = kwargs.get('verbose_name', None)

        # We want to skip ForeignObject in the MRO, so we can't use super here
        LayoutRelatedField.__init__(self, **kwargs)

    def get_other_model(self):
        """
        Returns the name of the model that this field points to. Subclasses of
        :class:`LayoutRelatedField` must implement this method.
        """
        raise NotImplementedError()

    def check(self, **kwargs):
        errors = LayoutRelatedField.check(self, **kwargs)
        for state in system_layout.allowed_values:
            with system_layout.as_value(state):
                if self.to is None:
                    # This should only happen if `cls` is not going to be used
                    # for `state`. Thus, we can skip all of these checks
                    continue
                state_errors = self._check_unique_target()
                for err in state_errors:
                    err.msg = 'With state {}: '.format(state) + err.msg
                errors.extend(state_errors)
        return errors

    def deconstruct(self):
        raise NotImplementedError()

    @property
    def related_fields(self):
        if self._related_fields is None:
            self._related_fields = self.resolve_related_fields()
        return self._related_fields

    def contribute_to_class(self, cls, name, virtual_only=False):
        # We need to skip RelatedField in the mro, so we can't use `super()`
        # here
        LayoutRelatedField.contribute_to_class(
            self, cls, name, virtual_only=virtual_only
        )
        setattr(cls, self.name, ReverseSingleRelatedObjectDescriptor(self))

    def contribute_to_related_class(self, cls, related):
        if not related.hidden and not related.related_model._meta.swapped:
            # This has to be idempotent so that it can be called once per
            # state
            if not hasattr(cls, related.get_accessor_name()):
                setattr(
                    cls, related.get_accessor_name(),
                    self.related_accessor_class()
                )
            getattr(cls, related.get_accessor_name()).related = related
            if related.limit_choices_to:
                cls._meta.related_fkey_lookups.append(
                    related.limit_choices_to
                )

class LayoutForeignKey(LayoutForeignObject, ForeignKey):
    """
    A version of :class:`django.db.models.fields.related.ForeignKey` that works
    for dynamic relations that point to different models depending on the
    layout of the current farm . The main difference between this class and
    `ForeignKey` is that the constructor does not accept the `to` attribute
    """
    empty_strings_allowed = False
    default_error_messages = {
        'invalid': _(
            '%(model)s instance with %(field)s %(value)r does not exist'
        )
    }
    description = _('Foreign Key (type determined by related field)')

    def __init__(self, to_field=None, rel_class=LayoutManyToOneRel, \
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
        LayoutForeignObject.__init__(self, ['self'], [to_field], **kwargs)

    def get_other_model(self):
        """
        Returns the name of the model that this field points to. Subclasses of
        :class:`LayoutRelatedField` must implement this method.
        """
        raise NotImplementedError()

    @cached_property
    def to_field(self): # pylint: disable=method-hidden
        """
        If :attr:`to_field` is not set in init, generate it and indicate to
        :meth:`_check_consistent_to_field` that it doesn't need to perform
        it's check.
        """
        self.generated_to_field = True
        for layout in system_layout.allowed_values:
            with system_layout.as_value(layout):
                if self.to is not None:
                    return self.to._meta.pk.name

    def check(self, **kwargs):
        errors = LayoutForeignObject.check(self, **kwargs)
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
        if self.to_field is None:
            return checks.Error(
                'LayoutForeignKey could not figure out what field to point to '
                'on the related model', hint=None, obj=self, id='fields.E312'
            )
        if 'generated_to_field' in self.__dict__ and self.generated_to_field:
            for state in system_layout.allowed_values:
                with system_layout.as_value(state):
                    if self.to is not None and (self.to._meta.pk and
                            self.to._meta.pk.name) != self.to_field:
                        model_name = self.to._meta.object_name
                        return [
                            checks.Error(
                                "LayoutForeignKey on model '%s' should point "
                                "to a different field in the target model "
                                "depending on the current state. This is "
                                "currently not supported." % model_name,
                                hint=None,
                                obj=self,
                                id='fields.E313',
                            )
                        ]
        return []

    def deconstruct(self):
        raise NotImplementedError()

    def contribute_to_related_class(self, cls, related):
        LayoutForeignObject.contribute_to_related_class(self, cls, related)
        if self.rel.field_name is None:
            self.rel.field_name = cls._meta.pk.name
