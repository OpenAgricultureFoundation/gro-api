import inspect
from django.db.models.base import Model, ModelBase

class DynamicModelBase(ModelBase):
    """
    Abstract metaclass for models whose behavior varies depending on some
    application state variable. Subclasses of :class:`DynamicModelBase` must
    define a class attribute :attr:`state_var` that is a
    :class:`cityfarm_api.state.StateVariable`...
    """
    @property
    def states(self):
        """
        A list of all of the application states for which this model would
        behave differently. Subclasses of
        :class:`~cityfarm_api.models.DynamicmModelBase` must implement this
        property.
        """
        return self.state_var.allowed_values()

    def add_to_class(cls, name, value):
        if not inspect.isclass(value):
            if hasattr(value, 'contribute_to_class'):
                value.contribute_to_class(cls, name)
            if hasattr(value, 'init_for_state'):
                for state in cls.states:
                    value.init_for_state(cls, name, state)
        else:
            setattr(cls, name, value)
