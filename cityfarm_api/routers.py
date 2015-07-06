"""
This module defines a single :class:`~rest_framework.routers.DefaultRouter`
subclass to be used for managing urls in this project.
"""
from rest_framework import routers, views, reverse, response

class HybridRouter(routers.DefaultRouter):
    """
    A :class:`~rest_framework.routers.DefaultRouter` subclass that can register
    view functions in addition to viewsets
    """
    def __init__(self, *args, **kwargs):
        super(HybridRouter, self).__init__(*args, **kwargs)
        self._api_view_urls = {}

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
        urls = super(HybridRouter, self).get_urls()
        for api_view_key in self._api_view_urls.keys():
            urls.append(self._api_view_urls[api_view_key])
        return urls

    def get_api_root_view(self):
        # Copy the following block from Default Router
        api_root_dict = {}
        list_name = self.routes[0].name
        for prefix, _, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)
        api_view_urls = self._api_view_urls

        class APIRoot(views.APIView):
            """ The view class to return """
            _ignore_model_permissions = True

            def get(self, request, **kwargs):
                """ Get the root view """
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
