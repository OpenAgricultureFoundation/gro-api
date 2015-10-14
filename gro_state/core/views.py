import logging
from rest_framework.views import exception_handler
from rest_framework.status import is_client_error

logger = logging.getLogger('django.request')

def my_exception_handler(exc, context):
    """
    Django REST handles 4xx exceptions itself, so they don't get logged to the
    'django.request' logger by default. This exception handler logs them as if
    Django was handling them then calls the default Django REST handler. This
    makes the project logging behavior more consistent (both 4xx's and 5xx's
    are sent to the 'django.request' logger)
    """
    res = default_exception_handler(exc, context)
    if res is not None and is_client_error(res.status_code):
        request = context['request']
        logger.warn(
            '%s (params: %s) (data: %s) (response: %s)', request.path,
            request.query_params, request.data, res.data,
            extra={
                'status_code': res.status_code, 'request': request
            }
        )
    return res
