from django.db import models
from django.conf import settings

if settings.NODE_TYPE == "ROOT":
    Base = models.Model
elif settings.NODE_TYPE == "LEAF":
    from solo.models import SingletonModel
    Base = SingletonModel
else:
    raise ImproperlyConfigured()

class Farm(Base):
    name = models.Charfield(max_length=100)
    subdomain = models.SlugField()
    layout = models.SlugField()
    ip = models.GenericIPAddressField()
