"""
This module defines a set of routines (sequences of commands) that will be
used by this app.
"""

import logging
from django.conf import settings
from control.commands import Command, Flush, migrate, ReloadWorkers
logger = logging.getLogger(__name__)


class Routine:
    """
    A base class for all routines in this module. Subclasses of this class
    must define an attribute :attr:`command_classes` which is a list of
    :class:`~control.commands.Command` subclasses to run for this routine. They
    should also define an attribute :attr:`title` which is the name of the
    routine being run.
    """
    #: The title of this routine
    title = 'Unnamed Routine'
    #: Whether or not a URL should be generated for this routine
    hidden = False

    def __init__(self):
        self.commands = [CommandCls() for CommandCls in self.command_classes]

    @classmethod
    def check(self):
        for command_class in self.command_classes:
            if not issubclass(command_class, Command):
                raise TypeError('Routine can only hold Command subclasses')

    def run(self):
        logger.info('Running routine "%s"', self.title)
        for command in self.commands:
            logger.info('Running command "%s"', command.title)
            command.run()

    def to_json(self):
        result = []
        for command in self.commands:
            logger.info('Running command "%s"', command.title)
            result.append(command.to_json())
        return result

class SetupLayout(Routine):
    hidden = True
    title = 'Setup Layout'
    command_classes = (migrate('layout', '0001'), migrate())


class Restart(Routine):
    title = 'Restart'
    command_classes = (ReloadWorkers,)


class Reset(Routine):
    title = 'Reset'
    command_classes = (Flush,) + tuple(migrate(app_name, 'zero') for app_name
            in settings.CITYFARM_API_APPS) + (migrate(),)
