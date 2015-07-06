"""
This module defines a set of global exceptions for the CityFARM API Django
project.
"""

from rest_framework.exceptions import APIException

class FarmNotConfiguredError(APIException):
    """
    This exception should be thrown when a user attempts to input data for a
    farm that has not yet been configured.
    """
    status_code = 403
    default_detail = (
        "Please configure your farm before attempting to save data in this API"
    )
