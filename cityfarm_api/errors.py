from django.core.exceptions import ImproperlyConfigured

class InvalidNodeType(ImproperlyConfigured):
    message = 'Invalid NODE_TYPE. Valid options are "leaf" and "root"'
    def __init__(self):
        super().__init__(self.message)
