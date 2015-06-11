"""
This module defines a set of routines (sequences of commands) that will be
used by this app.
"""

from control.commands import Command, ReloadWorkers, MakeMigrations, Migrate

class Routine:
    __all__ = set()
    def __init__(self, title, *command_classes):
        self.title = title
        for command_class in command_classes:
            if not issubclass(command_class, Command):
                raise TypeError("Routine can only hold Command subclasses")
        self.command_classes = command_classes
        self.__all__.add(self)
    @property
    def commands(self):
        return [command_class() for command_class in self.command_classes]
    def run(self):
        for command in self.commands:
            for item in command.run():
                yield item
Restart = Routine("Restart", MakeMigrations, Migrate, ReloadWorkers)
Test = Routine("Test", Migrate)
