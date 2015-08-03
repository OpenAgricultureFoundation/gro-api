from django.db import models
from cityfarm_api.models import Model, GenerateNameMixin
from farms.models import Farm
from resources.models import ResourceType, ResourceProperty, Resource

class ActuatorType(Model):
    name = models.CharField(max_length=100)
    resource_type = models.ForeignKey(
        ResourceType, related_name='actuator_types'
    )
    properties = models.ManyToManyField(
        ResourceProperty, related_name='actuator_types'
    )
    read_only = models.BooleanField(editable=False, default=False)
    def __str__(self):
        return self.name + (' (stock)' if self.read_only else ' (custom)')

class Actuator(GenerateNameMixin, Model):
    name = models.CharField(max_length=100, blank=True)
    actuator_type = models.ForeignKey(ActuatorType, related_name='actuators')
    resource = models.ForeignKey(Resource, related_name='actuators')

    def generate_name(self):
        farm_name = Farm.get_solo().name
        return "{} {} {}".format(
            farm_name, self.actuator_type.name, self.pk
        )

    def __str__(self):
        return self.name

class ActuatorState(Model):
    class Meta:
        ordering = ['timestamp']
        get_latest_by = 'timestamp'
    origin = models.ForeignKey(Actuator, related_name='state+')
    timestamp = models.IntegerField()
    value = models.FloatField()
