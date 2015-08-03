from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from cityfarm_api.models import Model, GenerateNameMixin
from farms.models import Farm

class ResourceType(Model):
    name = models.CharField(max_length=100)
    read_only = models.BooleanField(editable=False, default=False)
    def __str__(self):
        return self.name

class ResourceProperty(Model):
    code = models.CharField(max_length=2)
    name = models.CharField(max_length=100)
    resource_type = models.ForeignKey(ResourceType, related_name='properties')
    read_only = models.BooleanField(editable=False, default=False)
    def __str__(self):
        return "{} {}".format(self.resource_type.name, self.name)

class Resource(GenerateNameMixin, Model):
    name = models.CharField(max_length=100, blank=True)
    resource_type = models.ForeignKey(ResourceType, related_name='resources')
    location_type = models.ForeignKey(ContentType)
    location_id = models.PositiveIntegerField()
    location = GenericForeignKey('location_type', 'location_id')

    def generate_name(self):
        farm_name = Farm.get_solo().name
        return "{} {} {} {}".format(
            farm_name, self.resource_type.name, self.__class__.__name__,
            self.pk
        )

    def __str__(self):
        return self.name
