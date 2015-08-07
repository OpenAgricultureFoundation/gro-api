from django.db import models
from cityfarm_api.models import Model
from resources.models import ResourceType, ResourceProperty, Resource


class ActuatorTypeManager(models.Manager):
    def get_by_natural_key(self, type_code, actuator_code):
        resource_type = ResourceType.objects.get_by_natural_key(type_code)
        return self.get(code=actuator_code, resource_type=resource_type)


class ActuatorType(Model):
    class Meta:
        unique_together = (
            ('code', 'resource_type'), ('name', 'resource_type')
        )
        default_related_name = 'actuator_types'

    code = models.CharField(max_length=2)
    name = models.CharField(max_length=100)
    resource_type = models.ForeignKey(ResourceType)
    properties = models.ManyToManyField(ResourceProperty)
    order = models.PositiveIntegerField()
    is_binary = models.BooleanField()
    effect_on_active = models.IntegerField()
    read_only = models.BooleanField(editable=False, default=False)
    actuator_count = models.PositiveIntegerField(
        editable=False, default=0
    )

    objects = ActuatorTypeManager()

    def natural_key(self):
        return (self.resource_type.code, self.code)
    natural_key.dependencies = ['resources.ResourceType']

    def __str__(self):
        return self.name


class Actuator(Model):
    class Meta:
        unique_together = ('index', 'actuator_type')

    index = models.PositiveIntegerField(editable=False)
    name = models.CharField(max_length=100, blank=True)
    actuator_type = models.ForeignKey(ActuatorType, related_name='actuators')
    resource = models.ForeignKey(Resource, related_name='actuators')
    override_value = models.FloatField(editable=False, null=True)
    override_timeout = models.IntegerField(editable=False, null=True)

    def __str__(self):
        return self.name


class ActuatorState(Model):
    class Meta:
        ordering = ['timestamp']
        get_latest_by = 'timestamp'

    origin = models.ForeignKey(Actuator, related_name='state+')
    timestamp = models.IntegerField()
    value = models.FloatField()
