"""
This module defines a single :class:`~rest_framework.routers.DefaultRouter`
subclass to be used for managing urls in this project.
"""
import inspect
import logging
import importlib
from django.db import models
from django.apps import apps
from django.conf import settings
from django.utils.functional import cached_property
from rest_framework import routers, views, reverse, response
from layout.state import SystemLayout
from .models import Model
from .viewsets import model_viewsets

logger = logging.getLogger(__name__)

class BaseRouter(routers.DefaultRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api_view_urls = {}

    @classmethod
    def get_instance(cls, *args, **kwargs):
        """
        Gets an instance of this class populated with urls for the current farm
        layout. Instances are cached by layout.
        """
        internal_name = '_{}_router'.format(SystemLayout().current_value)
        if not hasattr(cls, internal_name):
            router = cls()
            for app_name in settings.CITYFARM_API_APPS:
                try:
                    # Try to use the `contribute_to_router` function in the
                    # `urls` submodule for app
                    app_urls = importlib.import_module('.urls', app_name)
                    app_urls.contribute_to_router(router)
                    # Also register the app normally if the `urls` submodule
                    # tells us to
                    if hasattr(app_urls, 'GENERATE_DEFAULT_ROUTES') and \
                            app_urls.GENERATE_DEFAULT_ROUTES:
                        router.register_app(app_name)
                except ImportError as err:
                    # App has no `urls` submodule`. Just register the app
                    # normally
                    router.register_app(app_name)
                except AttributeError as err:
                    logger.warn(
                        'Failed to load urls for app "%s". `urls` submodule '
                        'should define a function `contribute_to_router`.'
                        % app_name
                    )
            setattr(cls, internal_name, router)
        return getattr(cls, internal_name)

    def register_app(self, app_name):
        """ Register all of the models in the app with the given name """
        for model in apps.get_app_config(app_name).get_models():
            self.register_model(model)

    def register_model(self, model):
        """ Register the given model to this router """
        model_name = model._meta.object_name
        lower_model_name = model_name[0].lower() + model_name[1:]
        self.register(
            lower_model_name, model_viewsets.get_for_model(model)
        )

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
        # Copy the following block from Default Router
        api_root_dict = {}
        list_name = self.routes[0].name
        for prefix, _, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)
        api_view_urls = self._api_view_urls

        class APIRoot(views.APIView):
            _ignore_model_permissions = True

            def get(self, request, **kwargs):
                """ GET the root view """
                ret = {}
                for key, url_name in api_root_dict.items():
                    ret[key] = reverse.reverse(
                        url_name,
                        request=request,
                        format=kwargs.pop('format', None)
                    )
                # In addition to what had been added, now add the APIView urls
                for api_view_key in api_view_urls.keys():
                    ret[api_view_key] = reverse.reverse(
                        api_view_urls[api_view_key].name,
                        request=request,
                        format=kwargs.pop('format', None)
                    )
                return response.Response(ret)

        return APIRoot.as_view()
