"""
This module defines a set of utility functions that can be used by the apps in
this project
"""
from django.db.utils import OperationalError
from farms.models import Farm, DEFAULT_LAYOUT

def get_current_layout():
    """
    Get the layout of the current farm as a string.
    """
    try:
        return Farm.get_solo().layout
    except OperationalError:
        # The farm table hasn't been created yet. We should be either creating
        # or applying migrations. Just pretend there is a farm with the default
        # attributes for now
        return DEFAULT_LAYOUT
