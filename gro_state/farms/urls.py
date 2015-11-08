from .views import FarmViewSet

class MyLoginView(LoginView):
    def login(self):
        self.user = self.serializer.validated_data['user']
        self.token = self.token_model.objects.get(user=self.user)
        auth_login(self.request, self.user)

    def get(self, request, *args, **kwargs):
        form = AuthenticationForm(request)
        current_site = get_current_site(request)
        context = {
            'form': form,
            'site': current_site,
            'site_name': current_site.name,
        }
        return TemplateResponse(request, 'rest_framework/login.html', context)

auth_patterns = [
    # URLs that don't require auth
    url(r'^login/$', MyLoginView.as_view(), name='login'),
    url(r'^password/reset/$', PasswordResetView.as_view(),
        name='password_reset'),
    url(r'^password/reset/confirm/$', PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'),
    url(r'^registration/$', RegisterView.as_view(), name='register'),
    url(r'^registration/verify-email/$', VerifyEmailView.as_view(),
        name='verify_email'),
    url(r'^account-confirm-email/(?P<key>\w+)/$', TemplateView.as_view(),
        name='account_confirm_email'),
    # URLs that require auth
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^user/$', UserDetailsView.as_view(), name='user_details'),
    url(r'^password/change/$', PasswordChangeView.as_view(),
        name='password_change'),
]

def contribute_to_router(router, layout):
    if layout is None:
        router.register(r'farm', FarmViewSet)
    # if layout is None:
    #     urls = urls + [
    #         url(r'^auth/', include(auth_patterns, namespace='rest_framework')),
    #         #url(r'^auth/registration/', include('rest_auth.registration.urls')),
    #         url(r'^docs/', include('rest_framework_swagger.urls')),
    #     ]
