from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.response import TemplateResponse
from django.views.generic import TemplateView
from rest_auth.views import (
    LoginView, LogoutView, UserDetailsView, PasswordChangeView,
    PasswordResetView, PasswordResetConfirmView
)
from rest_auth.registration.views import RegisterView, VerifyEmailView
from .routers import BaseRouter

def get_urls_by_layout(layout):
    urls = BaseRouter.get_instance(layout).urls
    # TODO: do we need this?
    # urls += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if settings.DEBUG:
        import debug_toolbar
        urls.append(url(r'^__debug__/', include(debug_toolbar.urls)))
    return [url(r'api/', include(urls)), ]
