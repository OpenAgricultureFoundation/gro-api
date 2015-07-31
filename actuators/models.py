from django.db import models
from cityfarm_api.models import Model
from resources.models import Resource, ResourceProperty

class ActuatorType(Model):
    name = models.CharField(max_length=100)
    properties = models.ManyToManyField(
        ResourceProperty, related_name='actuator_types'
    )
    read_only = models.BooleanField(editable=False, default=False)
    def __str__(self):
        return self.name + (' (stock)' if self.read_only else ' (custom)')

class Actuator(Model):
    name = models.CharField(max_length=100)
    actuator_type = models.ForeignKey(ActuatorType, related_name='actuators')
    resource = models.ForeignKey(Resource, related_name='actuators')
    def __str__(self):
        return self.name

class ActuatorState(Model):
    class Meta:
        ordering = ['timestamp']
        get_latest_by = 'timestamp'
    origin = models.ForeignKey(Actuator, related_name='state+')
    timestamp = models.IntegerField()
    value = models.FloatField()
