"""
This module defines a set of routines (sequences of commands) that will be
used by this app.
"""

from control.commands import Command, ReloadWorkers, MakeMigrations, Migrate

all_routines = set()


def Routine(title, *command_classes):
    """
    Returns a Routine class that performs the given commands in sequence

    :param title: The title of the routine
    :param *command_classes: A list of command classes to be run in this Routine
    """
    for command_class in command_classes:
        if not issubclass(command_class, Command):
            raise TypeError('Routine can only hold Command subclasses')

    _title = title  # Scoping is weird
    _command_classes = command_classes  # Scoping is weird

    class Inner:
        title = _title

        def __init__(self):
            self.commands = [Command() for Command in _command_classes]

        def run(self):
            for command in self.commands:
                for item in command.run():
                    yield item

    all_routines.add(Inner)
    return Inner
Restart = Routine("Restart", MakeMigrations, Migrate, ReloadWorkers)
