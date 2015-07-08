"""
This module defines a base model class form which all models in this project
should inherit.
"""
import django.db.models as django_models
from django.conf import settings

class Model(django_models.Model):
    """
    Base model class from which all database models in this project should
    inherit. By default, these models will be managed only on leaf servers.
    """
    class Meta:
        abstract = True
        managed = settings.SERVER_TYPE == settings.LEAF
