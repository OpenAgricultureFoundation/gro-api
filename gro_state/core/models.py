"""
This module defines a base model class form which all models in this project
should inherit.
"""
from django.db import OperationalError
from django.db.models.base import ModelBase
from django.db.models.signals import post_migrate
from django.conf import settings
from django.dispatch import receiver
from solo import models as solo_models
from solo import settings as solo_settings
from .const import ServerType

class SingletonMetaClass(ModelBase):
    """
    A metaclass to use for singletons that automatically registers a
    post_migrate signal listener that tries to create the singleton instance
    """
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if not cls._meta.abstract:
            @receiver(post_migrate)
            def create_singleton_instance(sender, **kwargs):
                try:
                    cls.get_solo()
                except OperationalError:
                    pass

class SingletonModel(solo_models.SingletonModel, metaclass=SingletonMetaClass):
    """
    A singleton model to be used for any singletons in the project. It uses the
    SingletonMetaClass and is cached properly in both leaf and root server
    instances
    """
    class Meta:
        abstract = True

if settings.SERVER_TYPE == ServerType.ROOT:
    # TODO: Use environ instead of request cache because request cache doesn't
    # exist anymore
    from .middleware import get_request_cache
    @classmethod
    def get_singleton_cache_key(cls):
        request_cache = get_request_cache()
        farm = request_cache.get('farm')
        prefix = solo_settings.SOLO_CACHE_PREFIX
        return '{}:{}:{}'.format(prefix, farm, cls.__name__.lower())
    SingletonModel.get_cache_key = get_singleton_cache_key
