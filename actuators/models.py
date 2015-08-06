from django.db import models
from cityfarm_api.models import Model
from resources.models import ResourceType, ResourceProperty, Resource


class ActuatorTypeManager(models.Manager):
    def get_by_natural_key(self, code):
        return self.get(code=code)


class ActuatorType(Model):
    class Meta:
        default_related_name = 'actuator_types'

    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100, unique=True)
    resource_type = models.ForeignKey(ResourceType)
    properties = models.ManyToManyField(ResourceProperty)
    order = models.PositiveIntegerField()
    is_binary = models.BooleanField()
    effect_on_active = models.IntegerField()
    read_only = models.BooleanField(editable=False, default=False)
    actuator_creation_count = models.PositiveIntegerField(
        editable=False, default=1
    )

    objects = ActuatorTypeManager()

    def natural_key(self):
        return (self.code, )

    def __str__(self):
        return self.name


class Actuator(Model):
    class Meta:
        unique_together = ('index', 'actuator_type')

    index = models.PositiveIntegerField(editable=False)
    name = models.CharField(max_length=100, blank=True)
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
