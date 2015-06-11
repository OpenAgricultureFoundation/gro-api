class InvalidFilePath(Exception):
    """
    A base exception type for errors in which an invalid filepath is detected.
    Subclasses of this Exception must define the :attr:`message` attribute.
    """
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath


class InvalidFifoPath(InvalidFilePath):
    """
    This exception should be thrown if this server fails to find the Master FIFO
    file of the Django server to be controlled.
    """
    @property
    def message(self):
        return 'FIFO file "%s" does not exist' % self.filepath


class InvalidManagerPath(InvalidFilePath):
    """
    This exception should be thrown if this server fails to find the
    :file:`manage.py` file of the Django server to be controlled.
    """
    @property
    def message(self):
        return 'manage.py file "%s" does not exist' % self.filepath
