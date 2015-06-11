"""
This app defines a Flask server and a set of views that together give a Django
server the ability to control itself. The Flask control server in the
:mod:`~control.server` module can send commands to the Django project's uWSGI
server through it's Master FIFO and can call subcommands from it's
:file:`manage.py` file. The :mod:`~control.commands` module defines the set of
commands (either uWSGI Master FIFO commands or :file:`manage.py` subcommands)
that can be run. The :mod:`~control.routines` module defines a set of routines
(sequences of commands). The server in :mod:`~control.server` generates an
endpoint for each routine that performs that routine, and the
:mod:`~control.views` module contains a list of endpoints to be included in the
Django app, one for each routine in :mod:`~control.routines`, each of which
calls the corresponding endpoint in the control server.

This app also defines a Django management command :program:`manage.py
runcontrolserver` that runs the server from the :mod:`~control.server` module.
"""
