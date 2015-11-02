"""
This module defines a single :class:`~rest_framework.routers.DefaultRouter`
subclass to be used for managing urls in this project.
"""
import logging
import importlib
from collections import OrderedDict
from django.conf import settings
from django.utils.functional import cached_property
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class BaseRouter(DefaultRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api_view_urls = {}

    @classmethod
    def get_instance(cls, layout, *args, **kwargs):
        """
        Gets an instance of this class populated with urls for the current farm
        layout
        """
        instance = cls(*args, **kwargs)
        for app_name in settings.GRO_STATE_APPS:
            try:
                # Try to use the `contribute_to_router` function in the
                # `urls` submodule for app
                app_urls = importlib.import_module('.urls', app_name)
            except ImportError as err:
                module_name = "{}.{}".format(app_name, 'urls')
                if err.name == module_name:
                    # The app has no `urls` submodule
                    logger.info(err)
                    continue
                else:
                    raise
            if hasattr(app_urls, 'contribute_to_router'):
                app_urls.contribute_to_router(instance, layout)
            else:
                raise Exception(
                    'Failed to load urls for app "{}". `urls` submodule '
                    'should define a function '
                    '`contribute_to_router`.'.format(app_name)
                )
        return instance

    def add_api_view(self, name, url):
        """
        Register a :class:`~django.conf.urls.url` instance with the name `name`

        :param str name: The name of the view to register
        :param url: The :class:`~django.conf.urls.url` instance to register
        """
        self._api_view_urls[name] = url

    def remove_api_view(self, name):
        """
        Delete the API view named `name`

        :param str name: The name of the view to remove
        """
        del self._api_view_urls[name]

    @property
    def api_view_urls(self):
        """
        A dictionary mapping the names of registered api views to related
        :class:`~django.conf.urls.url` instances.
        """
        ret = {}
        ret.update(self._api_view_urls)
        return ret

    def get_urls(self):
        urls = super().get_urls()
        for api_view_key in self._api_view_urls.keys():
            urls.append(self._api_view_urls[api_view_key])
        return urls

    @cached_property
    def urls(self):
        return self.get_urls()

    def get_api_root_view(self):
        api_root_dict = {}
        list_name = self.routes[0].name
        for prefix, _, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)
        api_view_urls = self._api_view_urls

        class APIRoot(APIView):
            _ignore_model_permissions = True
            allow_on_unconfigured_farm = True

            def get(self, request, **kwargs):
                ret = {}
                for key, url_name in api_root_dict.items():
                    ret[key] = reverse(
                        url_name,
                        request=request,
                        format=kwargs.pop('format', None)
                    )
                for api_view_key in api_view_urls.keys():
                    ret[api_view_key] = reverse(
                        api_view_urls[api_view_key].name,
                        request=request,
                        format=kwargs.pop('format', None)
                    )
                return Response(OrderedDict(sorted(ret.items())))

        return APIRoot.as_view()
