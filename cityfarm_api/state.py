class StateVariable:
    """
    Abastraction of an application-level state variable. Subclasses of
    :class:`StateVariable` must define both :meth:`current_value` and
    :meth:`allowed_values`
    """
    def current_value(self):
        """
        Returns the current value of this state variable, as a string.
        Subclasses of :class:`StateVariable` must define this method.
        """
        raise NotImplementedError()
    def allowed_values(self):
        """
        Generates all of the allowed values of this state variable. Subclasses
        of :class:`StateVariable must define this method.
        """
        raise NotImplementedError()
