#!/usr/bin/env python3
"""
This server allows the routines defined in the :mod:`~control.routines` module
to be triggered by a GET request. It generates an endpoint for each routine in
:mod:`~control.routines` that triggers the corresponding routine. Each endpoint
is named based on the title of the routine. This module also reads from the
environment variable :envvar:`CITYFARM_API_SERVER_MODE` to determine whether or
not to run in debug mode.
"""

###################
# Imports & Setup #
###################

import os
import importlib
from slugify import slugify
from control.exceptions import InvalidFilePath
from control.commands import OutputItem, Command
from control.routines import Routine, all_routines

###################
# Command Classes #
###################

for Routine in all_routines:
    url_rule = "/" + slugify(Routine.title.lower())
    endpoint = Routine.title
    @app.route(url_rule, endpoint=endpoint)
    def route():
        return RoutineWrapper(Routine()).to_response()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
