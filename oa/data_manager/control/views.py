"""
This module defines a view function for each routine in
:mod:`~control.command.routines`. It stores them in a dictionary
:obj:`all_views` which maps routine slugs to corresponding view functions.
"""

from slugify import slugify
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view
from .routines import Routine
from .serializers import UserSerializer, PermissionSerializer


class UserViewSet(ModelViewSet):
    """ A user registered with the system """
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class PermissionViewSet(ModelViewSet):
    """ A permission that can be given to or revoked from a user """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


all_views = {}

for routine_class in Routine.__subclasses__():
    @api_view()
    def view_func(request, routine=routine_class()):
        return Response(routine.to_json())
    view_func.__doc__ == routine_class.__doc__
    all_views[slugify(routine_class.title.lower())] = view_func
