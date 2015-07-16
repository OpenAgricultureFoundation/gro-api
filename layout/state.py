from django.db.utils import OperationalError
from django.conf import settings
from django.utils.functional import cached_property
from cityfarm_api.state import StateVariable
from farms.models import Farm

class SystemLayout(StateVariable):
    """
    This state variable represents the layout of the current farm. The current
    value is read from the singleton farm instance.
    """
    @cached_property
    def allowed_values(self):
        current_value = self.get_current_value()
        if settings.SERVER_TYPE == settings.ROOT:
            return all_schemata.keys()
        else:
            return [current_value,]

    def get_current_value(self):
        try:
            return Farm.get_solo().layout
        except OperationalError:
            return None
