from django.db.utils import OperationalError
from farms.models import Farm, DEFAULT_LAYOUT

def get_current_layout():
    try:
        return Farm.get_solo().layout
    except OperationalError:
        # The farm table hasn't been created yet. We should be either creating
        # or applying migrations. Just pretend there is a farm with the default
        # attributes for now
        return DEFAULT_LAYOUT
