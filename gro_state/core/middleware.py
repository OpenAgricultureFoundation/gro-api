import logging
import requests
from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from rest_framework.views import APIView
from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny
from ..farms.models import Farm

logger = logging.getLogger('gro_state')

class FarmNotConfiguredError(APIException):
    """
    This exception should be thrown when a user attempts to input data for a
    model in farm that has not yet been configured.
    """
    status_code = 403
    default_detail = (
        'This farm is not yet configured. Run `gro_state configure_farm` to '
        'configure it'
    )

class IsConfiguredDescriptor:
    """
    Non-data descriptor used in FarmIsConfiguredMiddleware to determine whether
    or not a Farm is configured
    """
    def __get__(self, obj, cls=None):
        if settings.PARENT_SERVER is None or settings.DEBUG:
            is_configured = Farm.get_solo().layout is not None
            if is_configured:
                obj.is_configured = True
            return is_configured
        else:
            try:
                res = requests.get('http://127.0.0.1/status')
            except requests.exceptions.RequestException as e:
                logger.error('Error querying system status: %s', e)
                FarmNotConfiguredError.default_detail = (
                    'Failed to get system status. Something is broken.'
                )
                return False
            else:
                if res.status_code == 200:
                    is_configured = res.data['is_configured']
                    if is_configured:
                        obj.is_configured = True
                        return True
                    else:
                        message = res.data['message']
                        FarmNotConfiguredError.default_detail = message
                        return False
                else:
                    logger.error(
                        'System status query returned error (%d): "%s"',
                        res.status_code, res.data
                    )
                    FarmNotConfiguredError.default_detail = (
                        'Failed to get system status. Something is broken'
                    )
                    return False

class FarmIsConfiguredCheckMiddleware:
    """ Hides all views until the current farm is configured """
    is_configured = IsConfiguredDescriptor()

    def __init__(self):
        if self.is_configured:
            raise MiddlewareNotUsed()
        class FarmNotConfiguredView(APIView):
            permission_classes = (AllowAny, )
            def get(self, _):
                raise FarmNotConfiguredError()
            post = get
            put = get
            patch = get
            delete = get
        self.view = FarmNotConfiguredView.as_view()

    def process_view(self, request, *kwargs):
        if self.is_configured:
            return
        return self.view(request)

class FarmDbRouter:
    def db_for_read(self, model, **hints):
        # TODO: Read this from the environment because it should be passed in
        # on a per-request basis
        raise NotImplementedError()
