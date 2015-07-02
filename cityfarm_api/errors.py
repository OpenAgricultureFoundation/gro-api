from rest_framework.exceptions import APIException

class FarmNotConfiguredError(APIException):
    status_code = 403
    default_detail = ("Please configure your farm before attempting to save "
            "data in this API")
