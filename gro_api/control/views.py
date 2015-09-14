"""
This module defines a view function for each routine in
:mod:`~control.command.routines`. It stores them in a dictionary
:obj:`all_views` which maps routine slugs to corresponding view functions.
"""

from slugify import slugify
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from .routines import Routine
from .serializers import (
    UserSerializer, GroupSerializer, PermissionSerializer, TokenSerializer
)


class UserViewSet(ModelViewSet):
    """ A user registered with the system """
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser, ]


class GroupViewSet(ModelViewSet):
    """ A group of users assigned a set of permissions """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAdminUser, ]


class PermissionViewSet(ModelViewSet):
    """ A permission that can be given to or revoked from a user """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAdminUser, ]


class TokenViewSet(ModelViewSet):
    """ A token for logging in to the API """
    queryset = Token.objects.all()
    serializer_class = TokenSerializer
    permission_classes = [IsAdminUser, ]


all_views = {}

for routine_class in Routine.__subclasses__():
    def view_func(request, routine=routine_class()):
        return Response(routine.to_json())
    view_func.__name__ = routine_class.__name__
    view_func.__doc__ = routine_class.__doc__
    # We can't use `api_view` as a decorator because we can't call it until we
    # have set the __name__ and __doc__ of `view_func`. Thus, we explicitly
    # call `api_view` afterwards
    view_fun = permission_classes((IsAdminUser, ))(view_func)
    view_func = api_view()(view_func)
    all_views[slugify(routine_class.title.lower())] = view_func
