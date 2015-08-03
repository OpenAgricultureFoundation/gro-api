from django.db import models
from cityfarm_api.models import Model, GenerateNameMixin
from farms.models import Farm
from resources.models import ResourceType, ResourceProperty, Resource

class SensorType(Model):
    name = models.CharField(max_length=100)
    resource_type = models.ForeignKey(
        ResourceType, related_name='sensor_types'
    )
    properties = models.ManyToManyField(
        ResourceProperty, related_name='sensor_types'
    )
    read_only = models.BooleanField(editable=False, default=False)
    def __str__(self):
        return self.name + (' (stock)' if self.read_only else ' (custom)')

class Sensor(GenerateNameMixin, Model):
    name = models.CharField(max_length=100, blank=True)
    sensor_type = models.ForeignKey(SensorType, related_name='sensors')
    resource = models.ForeignKey(Resource, related_name='sensors')

    def generate_name(self):
        farm_name = Farm.get_solo().name
        return "{} {} {}".format(
            farm_name, self.sensor_type.name, self.pk
        )

    def __str__(self):
        return self.name + ' (' + self.sensor_type.name + ')'

class SensingPoint(Model):
    sensor = models.ForeignKey(Sensor, related_name='sensing_points')
    property = models.ForeignKey(
        ResourceProperty, related_name='sensing_points'
    )
    def __str__(self):
        return self.sensor.name + ' - ' + self.property.name

class DataPoint(Model):
    class Meta:
        ordering = ['timestamp']
        get_latest_by = 'timestamp'
    origin = models.ForeignKey(SensingPoint, related_name='data_points+')
    timestamp = models.IntegerField()
    value = models.FloatField()
