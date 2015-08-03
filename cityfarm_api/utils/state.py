from contextlib import contextmanager
from django.db.utils import OperationalError
from django.conf import settings
from django.utils.functional import cached_property
from .functional import Singleton
from layout.schemata import all_schemata

if settings.SERVER_TYPE == settings.LEAF:
    from django.core.cache import caches
    get_cache = lambda: caches['default']
else:
    # Use the per-request cache
    raise NotImplementedError()

class SystemLayout(metaclass=Singleton):
    """
    This is a state variable the represents the layout of the current farm. The
    current value is read from the singleton farm instance
    """
    cache_key = 'layout'

    def __init__(self):
        self.use_mock_value = False
        self.mock_value = None
        if hasattr(settings, 'SETUP_WITH_LAYOUT'):
            self.use_mock_value = True
            self.mock_value = settings.SETUP_WITH_LAYOUT

    @property
    def current_value(self):
        if self.use_mock_value:
            return self.mock_value
        cache = get_cache()
        if self.cache_key in cache:
            return cache.get(self.cache_key)
        from farms.models import Farm
        try:
            val = Farm.get_solo().layout
            cache.set(self.cache_key, val)
            return val
        except OperationalError:
            return None

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
    def __init__(self, name, **kwargs):
        # We really only want to access the keyword argument `default`, but we
        # need to differentiate between a None `default` and no default, so we
        # can't give the argument a default value, and we have to use a general
        # dict
        self.name = name
        if 'default' in kwargs:
            self.default = kwargs.pop('default')
        assert len(kwargs) == 0

    @property
    def internal_name(self):
        return "_{}_{}".format(system_layout.current_value, self.name)

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self
        if not hasattr(instance, self.internal_name):
            setattr(instance, self.internal_name, self.default())
        return getattr(instance, self.internal_name)

    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)

class LayoutDependentCachedProperty:
    """
    A property that coverts a method with a single argument, ``self`` into a
    property cached on the instance dependent on the layout of the current
    farm.
    """
    def __init__(self, func):
        self.name = func.__name__
        self.func = func
        self.__doc__ = getattr(func, '__doc__')

    @property
    def internal_name(self):
        return "_{}_{}".format(system_layout.current_value, self.name)

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self
        if not hasattr(instance, self.internal_name):
            setattr(instance, self.internal_name, self.func(instance))
        return getattr(instance, self.internal_name)

    def __set__(self, instance, value):
        # We define this function only so that instances of this class will be
        # data descriptors and can overshadow attributes by the same name in
        # the instance dictionary
        raise NotImplementedError()
