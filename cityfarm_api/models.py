"""
This module defines a base model class form which all models in this project
should inherit.
"""
import django.db.models as django_models
import django.db.models.base as django_model_bases
import django.db.models.options as django_model_options
from django.conf import settings
from .utils.state import system_layout, LayoutDependentAttribute

class DynamicOptions(django_model_options.Options):
    _relation_tree = LayoutDependentAttribute('relation_tree')

class ModelBase(django_model_bases.ModelBase):
    """
    :class:`django.db.models.options.Options` caches a property
    `_relation_tree` that needs to be layout-dependent in dynamic models. This
    metaclass fixes that problem in models who specify that they are dynamic.
    """
    def add_to_class(cls, name, value):
        if isinstance(value, django_model_options.Options):
            if hasattr(value.meta, 'is_dynamic'):
                is_dynamic = value.meta.is_dynamic
                del value.meta.is_dynamic
                if is_dynamic:
                    value.__class__ = DynamicOptions
        super().add_to_class(name, value)


class Model(django_models.Model):#, metaclass=ModelBase):
    """
    Base model class from which all database models in this project should
    inherit. By default, these models will be managed only on leaf servers.
    """
    class Meta:
        abstract = True
        managed = settings.SERVER_TYPE == settings.LEAF
