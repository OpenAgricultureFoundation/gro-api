"""
This module defines a set of routines (sequences of commands) that will be
used by this app.
"""

import logging
from .commands import Command, Flush, Migrate, ClearCaches, ReloadWorkers
logger = logging.getLogger(__name__)


class Routine:
    """
    Abstract base class for all routines in this module. Subclasses of this
    class must define an attribute :attr:`commands` which is a list of
    :class:`~control.commands.Command` instances to run for this routine. They
    should also define an attribute :attr:`title` which is the name of this
    routine.
    """
    #: The title of this routine
    title = 'Unnamed Routine'

    def __call__(self):
        logger.info('Running routine "%s"', self.title)
        for command in self.commands:
            command()

    @classmethod
    def check(self):
        for command in self.commands:
            if not isinstance(command, Command):
                raise TypeError('Routine can only hold Command instances')

    def to_json(self):
        logger.info('Running routine "%s"', self.title)
        return [command.to_json() for command in self.commands]


class Restart(Routine):
    """ Restart the server """
    title = 'Restart'
    commands = (ReloadWorkers(),)


class Reset(Routine):
    """ Reset the server and clear all data """
    title = 'Reset'
    commands = (
        Migrate('layout', '0001'), Flush(), ClearCaches(), Migrate(),
        ReloadWorkers()
    )
