from django.db import models
from cityfarm_api.models import Model
from resources.models import ResourceProperty, Resource

class SensorType(Model):
    name = models.CharField(max_length=100)
    properties = models.ManyToManyField(
        ResourceProperty, related_name='sensor_types'
    )
    def __str__(self):
        return self.name

class Sensor(Model):
    name = models.CharField(max_length=100)
    sensor_type = models.ForeignKey(SensorType, related_name='sensors')
    resource = models.ForeignKey(Resource, related_name='sensors')
    def __str__(self):
        return self.name

class SensingPoint(Model):
    sensor = models.ForeignKey(Sensor, related_name='sensing_points')
    property = models.ForeignKey(
        ResourceProperty, related_name='sensing_points'
    )

class DataPoint(Model):
    origin = models.ForeignKey(SensingPoint, related_name='data_points')
    value = models.FloatField()
