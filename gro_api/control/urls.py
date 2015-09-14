from django.conf.urls import url
from rest_auth import views as rest_auth_views
from .views import (
    all_views, UserViewSet, GroupViewSet, PermissionViewSet, TokenViewSet
)

def contribute_to_router(router):
    router.register(r'user', UserViewSet)
    router.register(r'group', GroupViewSet)
    router.register(r'permission', PermissionViewSet)
    router.register(r'token', TokenViewSet)
    for name, view in all_views.items():
        view_url = url(r'^{}/$'.format(name), view, name=name)
        router.add_api_view(name, view_url)
