from django.conf import settings
from django.conf.urls import include, url, patterns
from django.conf.urls.static import static
from django.views import generic as django_generic_views
from rest_auth import views as rest_auth_views
from rest_auth.registration import views as rest_auth_registration_views
from .routers import BaseRouter

### From rest_auth.urls

class LoginView(rest_auth_views.LoginView):
    allow_on_unconfigured_farm = True
class LogoutView(rest_auth_views.LogoutView):
    allow_on_unconfigured_farm = True
class UserDetailsView(rest_auth_views.UserDetailsView):
    allow_on_unconfigured_farm = True
class PasswordResetView(rest_auth_views.PasswordResetView):
    allow_on_unconfigured_farm = True
class PasswordResetConfirmView(rest_auth_views.PasswordResetConfirmView):
    allow_on_unconfigured_farm = True
class PasswordChangeView(rest_auth_views.PasswordChangeView):
    allow_on_unconfigured_farm = True

auth_patterns = patterns('',
    # URLs that do not require a session or valid token
    url(r'^password/reset/$', PasswordResetView.as_view(),
        name='rest_password_reset'),
    url(r'^password/reset/confirm/$', PasswordResetConfirmView.as_view(),
        name='rest_password_reset_confirm'),
    url(r'^login/$', LoginView.as_view(), name='rest_login'),
    # URLs that require a user to be logged in with a valid session / token.
    url(r'^logout/$', LogoutView.as_view(), name='rest_logout'),
    url(r'^user/$', UserDetailsView.as_view(), name='rest_user_details'),
    url(r'^password/change/$', PasswordChangeView.as_view(),
        name='rest_password_change'),
)


### From rest_auth.registration.urls

class RegisterView(rest_auth_registration_views.RegisterView):
    allow_on_unconfigured_farm = True
class VerifyEmailView(rest_auth_registration_views.VerifyEmailView):
    allow_on_unconfigured_farm = True
class TemplateView(django_generic_views.TemplateView):
    allow_on_unconfigured_farm = True

auth_registration_patterns = patterns( '',
    url(r'^$', RegisterView.as_view(), name='rest_register'),
    url(r'^verify-email/$', VerifyEmailView.as_view(), name='rest_verify_email'),
    url(r'^account-confirm-email/(?P<key>\w+)/$', TemplateView.as_view(),
        name='account_confirm_email'),
)

def get_current_urls():
    urls = BaseRouter.get_instance().urls + [
        url(r'^auth/', include(auth_patterns)),
        url(r'^auth/registration/', include(auth_registration_patterns)),
        url(r'^docs/', include('rest_framework_swagger.urls')),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if settings.DEBUG:
        import debug_toolbar
        urls.append(url(r'^__debug__/', include(debug_toolbar.urls)))
    return urls
