"""
This module defines a view function for each routine in
:mod:`~control.command.routines`. It stores them in a dictionary
:obj:`all_views` which maps routine slugs to corresponding view functions.
"""

from slugify import slugify
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .routines import Routine

all_views = {}

for routine_class in Routine.__subclasses__():
    @api_view()
    def view_func(request, routine=routine_class()):
        return Response(routine.to_json())
    all_views[slugify(routine_class.title.lower())] = view_func
