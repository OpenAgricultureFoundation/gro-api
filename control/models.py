import os
from django.core import checks
from .commands import fifo_path, manager_path, FifoCommand
from .routines import Routine
from .exceptions import InvalidFifoFile, InvalidFifoPath, InvalidManagerPath

@checks.register
def check_fifo_path(app_configs, **kwargs):
    errors = []
    try:
        FifoCommand.check()
    except InvalidFifoPath as e:
        msg = 'Failed to find FIFO file'
        hint = 'Check that $UWSGI_MASTER_FIFO points to the uWSGI Master FIFO'
        errors.append(checks.CheckMessage(checks.WARNING, msg, hint))
    except InvalidFifoFile as e:
        msg = 'FIFO file is invalid'
        hint = 'Make sure the file at "{}" is a valid FIFO'.format(fifo_path)
        errors.append(checks.CheckMessage(checks.WARNING, msg, hint))
    return errors

for routine in Routine.__subclasses__():
    @checks.register
    def check_routine(app_configs, **kwargs):
        errors = []
        try:
            routine.check()
        except TypeError as e:
            errors.append(checks.CheckMessage(checks.WARNING, str(e)))
        return errors

