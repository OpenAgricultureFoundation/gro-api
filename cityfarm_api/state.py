"""
This module defines a single class, :class:`StateVariable`.
"""
from contextlib import contextmanager
from .utils import Singleton

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
            print("Nested StateVariable as_value context managers")
            import pdb; pdb.set_trace()
        self.mock_value = value
        yield
        self.mock_value = old_mock_value
