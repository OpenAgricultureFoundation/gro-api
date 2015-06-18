from django.db import router
from django.db.models import Field, PositiveIntegerField
from django.db.models.fields import BLANK_CHOICE_DASH
from django.utils.encoding import smart_text
from django.utils.functional import cached_property, curry
from farms.models import Farm

from layout.schemata import all_schemata


class per_layout_cached_property:
    # TODO: On a LEAF server, we don't need a dictionary because it would only
    # have 1 key. On a ROOT server, we always need a dictionary
    """
    Decorator that converts a method with two arguments (``self`` and ``layout``
    into a property cached on the instance on a per-layout basis.
    """
    def __init__(self, func):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')
        self.name = func.__name__
        # Name of the internal dict holding values for this property
        self.internal_name = '__%s' % self.name

    def __get__(self, instance, _):
        if instance is None:
            return self
        if self.internal_name not in instance.__dict__:
            instance.__dict__[self.internal_name] = {}
        layout = Farm.get_solo().layout
        if not layout:
            return None
        if layout not in instance.__dict__[self.internal_name]:
            instance.__dict__[self.internal_name][layout] = self.func(instance)
        return instance.__dict__[self.internal_name][layout]


class DynamicForeignKey(PositiveIntegerField):
    description = "Layout Parent"
    allow_unsaved_instance_assignment = False

    def _check_choices(self):
        """
        Override this to disable static checking of dynamic choices
        """
        return []

    def contribute_to_class(self, cls, name, virtual_only=False):
        self.set_attributes_from_name(name)
        self.model = cls
        if virtual_only:
            cls._meta.add_field(self, virtual=True)
        else:
            cls._meta.add_field(self)
        setattr(cls, 'get_%s_display' % self.name,
                curry(cls._get_FIELD_display, field=self))
        setattr(cls, self.name, ParentObjectDescriptor(self))

    def validate(self, value, model_instance):
        print("VALIDATING layout.fields.DynamicForeignKey")
        super().validate(value, model_instance)
        if value is None:
            return
        using = router.db_for_read(
            model_instance.__class__,
            instance=model_instance,
        )
        qs = self.related_model._default_manager.using(using).filter(pk=value)
        if not qs.exists():
            raise ValidationError(
                self.error_messages['invalid'],
                code='invalid',
                params={
                    'model': self.parent_model_name, 'field': pk, 'value': value
                },
            )

    def get_attname(self):
        return '%s_id' % self.name

    @cached_property
    def related_fields(self):
        return self, self.related_model._meta.pk

    @property
    def model_name(self):
        return self.model._meta.model_name

    @property
    def related_model(self):
        raise NotImplementedError()

    @property
    def related_model_name(self):
        return self.related_model._meta.model_name

    def formfield(self, **kwargs):
        db = kwargs.pop('using', None)
        defaults = {
            'form_class': forms.ModelChoiceField,
            'queryset': self.related_model._default_manager.using(db),
        }
        defaults.update(kwargs)
        print(super().formfield(**defaults))
        return super().formfield(**defaults)

    @property
    def choices(self):
        raise NotImplementedError()

    def get_choices(self, include_blank=True, blank_choice=BLANK_CHOICE_DASH,
            limit_to_currently_related=False):
        choices = blank_choice if include_blank else []
        if self.related_model:
            queryset = self.related_model._default_manager.all()
            choices += [(x._get_pk_val(), smart_text(x)) for x in queryset]
        return choices


class ParentObjectDescriptor:
    """
    Accessor to the related object for a ParentField. Based on
    :class:`django.models.fields.related.ReverseSingleRelatedObjectDescriptor`.

    In the example::

        class Example(Model):
            attr = ParentField()

    `Example.attr` is a ParentObjectDescriptor
    """
    def __init__(self, field):
        self.field = field

    @per_layout_cached_property
    def cache_name(self):
        return self.field.get_cache_name()

    @per_layout_cached_property
    def RelatedObjectDoesNotExist(self):
        return type(
            'RelatedObjectDoesNotExist',
            (self.field.related_model.DoesNotExist, AttributeError),
            {}
        )

    def is_cached(self, instance):
        return hasattr(instance, self.cache_name)

    def get_queryset(self, **hints):
        manager = self.field.related_model._default_manager
        if not getattr(manager, 'use_for_related_fields', False):
            manager = self.field.related_model._base_manager
        return manager.db_manager(hints=hints).all()

    def get_prefetch_queryset(self, instances, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        queryset._add_hints(instances=instances[0])
        # TODO: Add filtering to reduce the size of this query (see
        # ReverseSingleRelatedObjectDescriptor.get_prefetch_queryset). It is
        # probably ok without filtering for now because we expect all instances
        # of related_model to have at least 1 child, making filtering
        # unnecessary, but we shouldn't always assume this.
        related_attr = self.field.get_foreign_related_value
        instance_attr = self.field.get_local_related_value
        return queryset, related_attr, instance_attr, True, self.cache_name

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self
        try:
            rel_obj = getattr(instance, self.cache_name)
        except AttributeError:
            val = self.field.get_local_related_value(instance)
            if None in val:
                rel_obj = None
            else:
                qs = self.get_queryset(instance=instance)
                params = {
                    rh_field.attname: getattr(instance, lh_field.attname)
                    for lh_field, rh_field in self.field.related_fields
                }
                qs = qs.filter(**params)
                rel_obj = qs.get()
        if rel_obj is None:
            raise self.RelatedObjectDoesNotExist(
                "%s has no %s." % (self.field.model.__name__, self.field.name)
            )
        else:
            return rel_obj

    def __set__(self, instance, value):
        if value is None and self.field.null is False:
            raise ValueError(
                'Cannot assign None: "%s.%s" does not allow null values.' %
                (instance._meta.object_name, self.field.name)
            )
        elif value is not None and not isinstance(value, self.field.related_model):
            raise ValueError(
                'Cannot assign "%r": "%s.%s" must be a "%s" instance.' % (
                    value,
                    instance._meta.object_name,
                    self.field.name,
                    self.field.related_model_name,
                )
            )
        elif value is not None:
            if instance._state.db is None:
                instance._state.db = router.db_for_write(
                    instance.__class__, instance=value
                )
            elif value._state.db is None:
                value._state.db = router.db_for_write(
                    value.__class__, instance=instance
                )
            else:
                if not router.allow_relation(value, instance):
                    raise ValueError(
                        'Cannot assign "%r": the current database router '
                        'prevents this relation.' % value
                    )
        lh_field, rh_field = self.field.related_fields
        if value is None:
            setattr(instance, lh_field.attname, None)
        else:
            pk = value._get_pk_val()
            if not self.field.allow_unsaved_instance_assignment and pk is None:
                raise ValueError(
                    'Cannot assign "%s": "%s" instance isn\'t saved in the '
                    'database.' % (value, self.field.related_model_name)
                )
            setattr(
                instance, lh_field.attname, getattr(value, rh_field.attname)
            )
        setattr(instance, self.cache_name, value)

class DynamicRelation(Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.column = None
        self.concrete = False
        self.editable = False

    def contribute_to_class(self, cls, name, virtual_only=False):
        self.name = name
        self.attname = name
        self.model = cls
        cls._meta.add_field(self, virtual=True)
        setattr(cls, name, self)

    @property
    def model_name(self):
        return self.model._meta.model_name

    @property
    def related_model(self):
        raise NotImplementedError()

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self
        qs = self.related_model._default_manager.all()
        qs = qs.filter(**{self.remote_field_name: instance.pk})
        return qs.all()
