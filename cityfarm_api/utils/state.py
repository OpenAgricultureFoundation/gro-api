from contextlib import contextmanager
from django.db.utils import OperationalError
from django.core.cache import cache
from django.conf import settings
from django.utils.functional import cached_property
from .functional import Singleton
from layout.schemata import all_schemata

class SystemLayout(metaclass=Singleton):
    """
    This is a state variable the represents the layout of the current farm. The
    current value is read from the singleton farm instance
    """
    cache_key = 'system_layout'
    cache_timeout = 30  # 30 seconds

    def __init__(self):
        self.use_mock_value = False
        self.mock_value = None

    @property
    def current_value(self):
        if self.use_mock_value:
            return self.mock_value
        val = cache.get(self.cache_key)
        if val is None:
            from farms.models import Farm
            try:
                val = Farm.get_solo().layout
                cache.set(self.cache_key, val, self.cache_timeout)
            except OperationalError:
                pass
        return val

    @cached_property
    def allowed_values(self):
        if settings.SERVER_TYPE == settings.ROOT:
            return all_schemata.keys()
        else:
            if self.current_value is None:
                return all_schemata.keys()
            else:
                return [self.current_value, ]

    @contextmanager
    def as_value(self, value):
        had_mock_value = self.use_mock_value
        old_mock_value = self.mock_value
        self.use_mock_value = True
        self.mock_value = value
        yield
        self.use_mock_value = had_mock_value
        self.mock_value = old_mock_value

system_layout = SystemLayout()

class LayoutDependentAttribute:
    """
    A descriptor that behaves like an attribute but stores a different value
    depending on the layout of the current farm.
    """
    def __init__(self, name, default=None):
        self.name = name
        self.default = default

    @property
    def internal_name(self):
        return "_{}_{}".format(system_layout.current_value, self.name)

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self
        if system_layout.current_value is None:
            return self.default
        else:
            return getattr(instance, self.internal_name, None)

    def __set__(self, instance, value):
        if system_layout.current_value is not None:
            setattr(instance, self.internal_name, value)

class LayoutDependentCachedProperty:
    """
    A property that coverts a method with a single argument, ``self`` into a
    property cached on the instance dependent on the layout of the current
    farm.
    """
    def __init__(self, func, default=None):
        self.name = func.__name__
        self.func = func
        self.__doc__ = getattr(func, '__doc__')
        self.default = default

    @property
    def internal_name(self):
        return "_{}_{}".format(system_layout.current_value, self.name)

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self
        if system_layout.current_value is None:
            return self.default
        if not hasattr(instance, self.internal_name):
            setattr(instance, self.internal_name, self.func(instance))
        return getattr(instance, self.internal_name)
