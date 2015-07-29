from django.db import models
from cityfarm_api.models import Model
from resources.models import Resource, ResourceProperty

class ActuatorType(Model):
    name = models.CharField(max_length=100)
    properties = models.ManyToManyField(
        ResourceProperty, related_name='actuator_types'
    )
    def __str__(self):
        return self.name

class Actuator(Model):
    name = models.CharField(max_length=100)
    actuator_type = models.ForeignKey(ActuatorType, related_name='actuators')
    resource = models.ForeignKey(Resource, related_name='actuators')
    def __str__(self):
        return self.name
