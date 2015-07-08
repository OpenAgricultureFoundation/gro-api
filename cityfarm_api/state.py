"""
This module defines a single class, :class:`StateVariable`.
"""

class StateVariable:
    """
    Abastraction of an application-level state variable. Subclasses of
    :class:`StateVariable` must define both :meth:`current_value` and
    :meth:`allowed_values`
    """
    @staticmethod
    def current_value():
        """
        Returns the current value of this state variable, as a string.
        Subclasses of :class:`StateVariable` must define this method.
        """
        raise NotImplementedError()
    @staticmethod
    def allowed_values():
        """
        Generates all of the allowed values of this state variable. Subclasses
        of :class:`StateVariable must define this method.
        """
        raise NotImplementedError()
