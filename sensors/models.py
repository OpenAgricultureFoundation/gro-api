import time
from django.db import models
from cityfarm_api.models import Model
from resources.models import ResourceType, ResourceProperty, Resource


class SensorTypeManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class SensorType(Model):
    class Meta:
        default_related_name = 'sensor_types'

    name = models.CharField(max_length=100, unique=True)
    resource_type = models.ForeignKey(ResourceType)
    properties = models.ManyToManyField(ResourceProperty)
    sensor_count = models.PositiveIntegerField(
        editable=False, default=0
    )

    objects = SensorTypeManager()

    def natural_key(self):
        return (self.name, )

    def __str__(self):
        return self.name


class Sensor(Model):
    class Meta:
        unique_together =  ('index', 'sensor_type')
        default_related_name = 'sensors'

    index = models.PositiveIntegerField(editable=False)
    name = models.CharField(max_length=100, blank=True)
    sensor_type = models.ForeignKey(SensorType)
    resource = models.ForeignKey(Resource)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class SensingPoint(Model):
    class Meta:
        unique_together = ('index', 'property')
        default_related_name = 'sensing_points'

    index = models.PositiveIntegerField(editable=False)
    sensor = models.ForeignKey(Sensor, null=True)
    property = models.ForeignKey(ResourceProperty)
    is_active = models.BooleanField(default=True)
    is_pseudo = models.BooleanField(default=True)
    auto_created = models.BooleanField(editable=False, default=False)

    def __str__(self):
        return self.sensor.name + ' - ' + self.property.name


class DataPoint(Model):
    class Meta:
        ordering = ['timestamp']
        get_latest_by = 'timestamp'

    origin = models.ForeignKey(SensingPoint, related_name='data_points+')
    timestamp = models.IntegerField(blank=True, default=time.time)
    value = models.FloatField()
