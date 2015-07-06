"""
This module defines a base model class that all models in this project should
inherit from.
"""
import django.db.models as django_models
from django.conf import settings

class Model(django_models.Model):
    """
    Base model class from which all database models in this project should
    inherit.
    """
    class Meta:
        abstract = True
        managed = settings.SERVER_TYPE == settings.LEAF
