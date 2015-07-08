"""
This module defines a set of routines (sequences of commands) that will be
used by this app.
"""

import logging
from control.commands import Command, ReloadWorkers, MakeMigrations, Migrate
logger = logging.getLogger('cityfarm_api.control')


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

    def __init__(self):
        self.commands = [CommandCls() for CommandCls in self.command_classes]

    @classmethod
    def check(self):
        for command_class in self.command_classes:
            if not issubclass(command_class, Command):
                raise TypeError('Routine can only hold Command subclasses')

    def to_json(self):
        result = []
        for command in self.commands:
            logger.info('Running command "{}"'.format(command.title))
            result.append(command.to_json())
        return result


class Restart(Routine):
    title = 'Restart'
    command_classes = [MakeMigrations, MakeMigrations, Migrate, ReloadWorkers]
