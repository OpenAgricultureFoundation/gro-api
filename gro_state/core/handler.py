import sys
import types
import logging
from threading import local
from django import http
from django.conf import settings
from django.core import signals, urlresolvers
from django.core.handlers.base import BaseHandler
from django.core.exceptions import (
    PermissionDenied, SuspiciousOperation,
)
from django.http.multipartparser import MultiPartParserError
from django.utils import lru_cache
from django.utils.encoding import force_text
from django.views import debug
from rest_framework_swagger.urlparser import UrlParser
from .urls import get_urls_by_layout
from .utils import get_farm_from_request, get_layout_from_farm
from ..farms.models import Farm

_farm = local()

request_logger = logging.getLogger('django.request')

class FakeURLConfModule:
    def __init__(self, urls):
        self.urlpatterns = urls

@lru_cache.lru_cache(maxsize=None)
def get_resolver_by_layout(layout):
    return urlresolvers.RegexURLResolver(
        r'^/', FakeURLConfModule(get_urls_by_layout(layout))
    )

def get_resolver_by_urlconf(urlconf):
    # the urlconf should never actually change, but we need this to replace the
    # old get_resolver function
    return get_resolver_by_layout(_farm.layout)

def my_get_response(self, request):
    # There must be a default resolver in case there is an error before _layout
    # is computed
    resolver = get_resolver_by_layout(None)

    try:
        # Set the value of _layout for the current thread
        _farm.slug = get_farm_from_request(request)
        _farm.layout = _farm.slug and get_layout_from_farm(_farm.slug)

        resolver = get_resolver_by_layout(_farm.layout)

        response = None
        # Apply request middleware
        for middleware_method in self._request_middleware:
            response = middleware_method(request)
            if response:
                break

        if response is None:
            resolver_match = resolver.resolve(request.path_info)
            callback, callback_args, callback_kwargs = resolver_match
            request.resolver_match = resolver_match

            # Apply view middleware
            for middleware_method in self._view_middleware:
                response = middleware_method(request, callback, callback_args, callback_kwargs)
                if response:
                    break

        if response is None:
            wrapped_callback = self.make_view_atomic(callback)
            try:
                response = wrapped_callback(request, *callback_args, **callback_kwargs)
            except Exception as e:
                # If the view raised an exception, run it through exception
                # middleware, and if the exception middleware returns a
                # response, use that. Otherwise, reraise the exception.
                for middleware_method in self._exception_middleware:
                    response = middleware_method(request, e)
                    if response:
                        break
                if response is None:
                    raise

        # Complain if the view returned None (a common error).
        if response is None:
            if isinstance(callback, types.FunctionType):    # FBV
                view_name = callback.__name__
            else:                                           # CBV
                view_name = callback.__class__.__name__ + '.__call__'
            raise ValueError("The view %s.%s didn't return an HttpResponse object. It returned None instead."
                             % (callback.__module__, view_name))

        # If the response supports deferred rendering, apply template
        # response middleware and then render the response
        if hasattr(response, 'render') and callable(response.render):
            for middleware_method in self._template_response_middleware:
                response = middleware_method(request, response)
                # Complain if the template response middleware returned None (a common error).
                if response is None:
                    raise ValueError(
                        "%s.process_template_response didn't return an "
                        "HttpResponse object. It returned None instead."
                        % (middleware_method.__self__.__class__.__name__))
            response = response.render()

    except http.Http404 as e:
        request_logger.warning('Not Found: %s', request.path,
                    extra={
                        'status_code': 404,
                        'request': request
                    })
        if settings.DEBUG:
            response = debug.technical_404_response(request, e)
        else:
            response = self.get_exception_response(request, resolver, 404)

    except PermissionDenied:
        request_logger.warning(
            'Forbidden (Permission denied): %s', request.path,
            extra={
                'status_code': 403,
                'request': request
            })
        response = self.get_exception_response(request, resolver, 403)

    except MultiPartParserError:
        request_logger.warning(
            'Bad request (Unable to parse request body): %s', request.path,
            extra={
                'status_code': 400,
                'request': request
            })
        response = self.get_exception_response(request, resolver, 400)

    except SuspiciousOperation as e:
        # The request logger receives events for any problematic request
        # The security logger receives events for all SuspiciousOperations
        security_logger = logging.getLogger('django.security.%s' %
                        e.__class__.__name__)
        security_logger.error(
            force_text(e),
            extra={
                'status_code': 400,
                'request': request
            })
        if settings.DEBUG:
            return debug.technical_500_response(request, *sys.exc_info(), status_code=400)

        response = self.get_exception_response(request, resolver, 400)

    except SystemExit:
        # Allow sys.exit() to actually exit. See tickets #1023 and #4701
        raise

    except:  # Handle everything else.
        # Get the exception info now, in case another exception is thrown later.
        signals.got_request_exception.send(sender=self.__class__, request=request)
        response = self.handle_uncaught_exception(request, resolver, sys.exc_info())

    try:
        # Apply response middleware, regardless of the response
        for middleware_method in self._response_middleware:
            response = middleware_method(request, response)
            # Complain if the response middleware returned None (a common error).
            if response is None:
                raise ValueError(
                    "%s.process_response didn't return an "
                    "HttpResponse object. It returned None instead."
                    % (middleware_method.__self__.__class__.__name__))
        response = self.apply_response_fixes(request, response)
    except:  # Any exception should be gathered and handled
        signals.got_request_exception.send(sender=self.__class__, request=request)
        response = self.handle_uncaught_exception(request, resolver, sys.exc_info())

    response._closable_objects.append(request)

    if hasattr(_farm, 'slug'):
        del _farm.slug
    if hasattr(_farm, 'layout'):
        del _farm.layout

    return response

def my_get_apis(self, patterns=None, urlconf=None, filter_path=None, exclude_namespaces=[]):
    real_urlconf = FakeURLConfModule(get_urls_by_layout('tray'))
    return self.old_get_apis(
        patterns, real_urlconf, filter_path, exclude_namespaces
    )

def patch_handler():
    BaseHandler.get_response = my_get_response
    urlresolvers.get_resolver = get_resolver_by_urlconf
    UrlParser.old_get_apis = UrlParser.get_apis
    UrlParser.get_apis = my_get_apis
