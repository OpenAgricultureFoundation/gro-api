"""
This module defines a single class, :class:`StateVariable`.
"""
from contextlib import contextmanager
from django.db.utils import OperationalError
from django.conf import settings
from django.utils.functional import cached_property
from .utils import Singleton
from farms.models import Farm

class StateVariable(metaclass=Singleton):
    """
    Abstraction of an application-level state variable. Subclasses of
    :class:`StateVariable` must define a method :meth:`get_current_value` that
    returns the current value of the state variable and a class attribute
    :attr:`allowed_values` that is a list of all of the allowed values for this
    variable.
    """
    def __init__(self):
        self.mock_value = None

    @property
    def current_value(self):
        # TODO: Implement per-request caching
        return self.mock_value or self.get_current_value()

    def get_current_value(self):
        raise NotImplementedError()

    @contextmanager
    def as_value(self, value):
        old_mock_value = self.mock_value
        if old_mock_value and old_mock_value != value:
            logger.warn("Nested StateVariable as_value context managers")
        self.mock_value = value
        yield
        self.mock_value = old_mock_value


class SystemLayout(StateVariable):
    """
    This state variable represents the layout of the current farm. The current
    value is read from the singleton farm instance.
    """
    def __init__(self):
        super().__init__()
        if hasattr(settings, 'MOCK_SYSTEM_LAYOUT'):
            self.mock_value = getattr(settings, 'MOCK_SYSTEM_LAYOUT')

    @cached_property
    def allowed_values(self):
        if settings.SERVER_TYPE == settings.ROOT:
            return all_schemata.keys()
        else:
            return [self.current_value, ]

    def get_current_value(self):
        try:
            return Farm.get_solo().layout
        except OperationalError:
            return None
