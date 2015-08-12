from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from cityfarm_api.models import Model


class ResourceTypeManager(models.Manager):
    def get_by_natural_key(self, code):
        return self.get(code=code)


class ResourceType(Model):
    code = models.CharField(max_length=1, unique=True)
    name = models.CharField(max_length=100, unique=True)
    resource_count = models.PositiveIntegerField(
        editable=False, default=0
    )

    objects = ResourceTypeManager()

    def natural_key(self):
        return (self.code, )

    def __str__(self):
        return self.name


class ResourcePropertyManager(models.Manager):
    def get_by_natural_key(self, type_code, property_code):
        resource_type = ResourceType.objects.get_by_natural_key(type_code)
        return self.get(resource_type=resource_type, code=property_code)


class ResourceProperty(Model):
    class Meta:
        unique_together = (
            ('code', 'resource_type'), ('name', 'resource_type')
        )
        default_related_name = 'properties'

    code = models.CharField(max_length=2)
    name = models.CharField(max_length=100)
    resource_type = models.ForeignKey(ResourceType)
    min_operating_value = models.FloatField()
    max_operating_value = models.FloatField()
    sensing_point_count = models.PositiveIntegerField(
        editable=False, default=0
    )

    objects = ResourcePropertyManager()

    def natural_key(self):
        return (self.resource_type.code, self.code)
    natural_key.dependencies = ['resources.ResourceType']

    def __str__(self):
        return self.resource_type.name + ' ' + self.name


class Resource(Model):
    class Meta:
        unique_together = ('index', 'resource_type')
        default_related_name = 'resources'

    index = models.PositiveIntegerField(editable=False)
    name = models.CharField(max_length=100, blank=True)
    resource_type = models.ForeignKey(ResourceType)
    location_type = models.ForeignKey(ContentType)
    location_id = models.PositiveIntegerField()
    location = GenericForeignKey('location_type', 'location_id')

    def __str__(self):
        return self.name
