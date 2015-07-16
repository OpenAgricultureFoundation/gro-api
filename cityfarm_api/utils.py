"""
This module defines a set of utility functions that can be used by the apps in
this project
"""
from django.db.utils import OperationalError
from farms.models import Farm, DEFAULT_LAYOUT

class ModelDict(dict):
    """
    :class:`dict` subclass that can use model classes as keys. Internally it
    generates a tuple that uniquely identifies the model and uses that as a key
    because the model class itself is not hashable.
    """
    def __getitem__(self, model):
        return dict.__getitem__(self, self.get_key_for_model(model))

    def __setitem__(self, model, val):
        dict.__setitem__(self, self.get_key_for_model(model), val)

    def __contains__(self, item):
        return dict.__contains__(self, self.get_key_for_model(item))

    def get_key_for_model(self, model):
        return (model._meta.app_label, model._meta.object_name)

class Singleton(type):
    def __init__(cls, name, bases, dict):
        super().__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__call__(*args, **kwargs)
        return cls.instance
