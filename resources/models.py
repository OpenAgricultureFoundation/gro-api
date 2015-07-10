from django.db import models
from cityfarm_api.models import Model

class ResourceType(Model):
    name = models.CharField(max_length=100)
    read_only = models.BooleanField(editable=False, default=False)

class ResourceProperty(Model):
    name = models.CharField(max_length=100)
    resource_type = models.ForeignKey(ResourceType, related_name='properties')
    read_only = models.BooleanField(editable=False, default=False)

class Resource(Model):
    name = models.CharField(max_length=100)
    resource_type = models.ForeignKey(ResourceType, related_name='resources')
