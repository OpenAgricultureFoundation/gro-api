from django.db import models
from cityfarm_api.models import Model
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

class Sensor(Model):
    name = models.CharField(max_length=100, blank=True)
    sensor_type = models.ForeignKey(SensorType, related_name='sensors')
    resource = models.ForeignKey(Resource, related_name='sensors')
    def save(self, *args, **kwargs):
        res = super().save(*args, **kwargs)
        farm_name = Farm.get_solo().name
        if self._meta.get_field('name') and not self.name and farm_name:
            self.name = "{} {} {}".format(
                farm_name,
                self.__class__.__name__,
                self.pk
            )
            if 'force_insert' in kwargs and kwargs['force_insert']:
                kwargs['force_insert'] = False
            res = super().save(*args, **kwargs)
        return res

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
