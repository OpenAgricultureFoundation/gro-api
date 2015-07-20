from cityfarm_api.state import system_layout
from cityfarm_api.urls import get_current_urls
from django.conf import settings
from django.core import urlresolvers
from django.core.handlers.base import BaseHandler
from django.utils import lru_cache

class FakeURLConfModule:
    def __init__(self, urls):
        self.urlpatterns = urls

@lru_cache.lru_cache(maxsize=None)
def inner_get_resolver(urlconf, layout):
    return urlresolvers.RegexURLResolver(
        r'^/', FakeURLConfModule(get_current_urls())
    )

def outer_get_resolver(urlconf):
    return inner_get_resolver(urlconf, system_layout.current_value)

urlresolvers.get_resolver = outer_get_resolver

# Monkey patching `django.core.urlresolvers.get_resolver` doesn't completely
# solve the problem in Django 1.8.3 because
# `django.core.handlers.base.BaseHandler` creates a new
# `django.core.urlresolvers.RegexURLResolver` on every request. This is
# addressed by ticket #14200 (https://code.djangoproject.com/ticket/14200).
# A patch for this problem has been written and accepted, and should appear in
# the next Django release. Until then, we essentially apply the accepted patch
# ourselves by monkey patching `BaseHandler.get_response`.
def new_get_response(self, request):
    # Setup default url resolver for this thread, this code is outside
    # the try/except so we don't get a spurious "unbound local
    # variable" exception in the event an exception is raised before
    # resolver is set
    urlconf = settings.ROOT_URLCONF
    urlresolvers.set_urlconf(urlconf)
    resolver = urlresolvers.get_resolver(urlconf)
    try:
        response = None
        # Apply request middleware
        for middleware_method in self._request_middleware:
            response = middleware_method(request)
            if response:
                break

        if response is None:
            if hasattr(request, 'urlconf'):
                # Reset url resolver with a custom urlconf.
                urlconf = request.urlconf
                urlresolvers.set_urlconf(urlconf)
                resolver = urlresolvers.get_resolver(urlconf)

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
        logger.warning('Not Found: %s', request.path,
                    extra={
                        'status_code': 404,
                        'request': request
                    })
        if settings.DEBUG:
            response = debug.technical_404_response(request, e)
        else:
            response = self.get_exception_response(request, resolver, 404)

    except PermissionDenied:
        logger.warning(
            'Forbidden (Permission denied): %s', request.path,
            extra={
                'status_code': 403,
                'request': request
            })
        response = self.get_exception_response(request, resolver, 403)

    except MultiPartParserError:
        logger.warning(
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

    return response

BaseHandler.get_response = new_get_response
