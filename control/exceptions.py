"""
This module defines a set of exceptions that can be thrown during the execution
of the commands in the :mod:`~control.commands` module.
"""

from rest_framework.exceptions import APIException


class InvalidFile(APIException):
    """
    A base exception for errors in which an invalid file or filepath is
    encountered. Subclasses of this exception must define the arribute
    :attr:`detail` and can read from the attribute :attr:`filepath`, which is
    the offending filepath.

    :param str filepath: The of the file for which this error was thrown
    """
    status_code = 500

    def __init__(self, filepath):
        self.filepath = filepath


class InvalidFifoPath(InvalidFile):
    """
    This exception should be thrown if the filepath designated as the path of
    the uWSGI Master FIFO is determined to be invalid.
    """
    @property
    def detail(self):
        return 'FIFO file "%s" does not exist' % self.filepath


class InvalidFifoFile(InvalidFile):
    """
    This exception should be thrown if the filepath designated as the path of
    the uWSGI Master FIFO points to a file that is invalid. This could occur if
    the file is not a pipe or if it is not being read from.
    """
    @property
    def detail(self):
        return 'FIFO file "%s" is invalid' % self.filepath


class InvalidManagerPath(InvalidFile):
    """
    This exception should be thrown if the filepath designated as the path of
    the :file:`manage.py` file of the server is determined to be invalid.

    """
    @property
    def detail(self):
        return 'manage.py file "%s" does not exist' % self.filepath
