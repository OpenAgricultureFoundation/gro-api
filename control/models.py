import os
from django.core import checks
from .commands import fifo_path, manager_path, FifoCommand, ManagerCommand
from .exceptions import InvalidFifoPath, InvalidManagerPath

@checks.register
def check_fifo_path(app_configs, **kwargs):
    errors = []
    try:
        FifoCommand.check()
    except InvalidFifoPath as e:
        msg = 'Failed to find FIFO file at {}'.format(fifo_path)
        hint = 'Check that $UWSGI_MASTER_FIFO points to the uWSGI Master FIFO'
        errors.append(checks.CheckMessage(checks.WARNING, msg, hint, fifo_path))
    return errors

@checks.register
def check_manager_path(app_configs, **kwargs):
    errors = []
    try:
        ManagerCommand.check()
    except InvalidManagerPath as e:
        msg = 'Failed to find manage.py file at {}'.format(manager_path)
        errors.append(checks.CheckMessage(checks.WARNING, msg, None, fifo_path))
    return errors
