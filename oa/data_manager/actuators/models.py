import time
from django.db import models
from ..resources.models import (
    ResourceType, ResourceProperty, ResourceEffect, Resource
)


class ActuatorTypeManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class ActuatorType(models.Model):
    class Meta:
        default_related_name = 'actuator_types'

    name = models.CharField(max_length=100)
    resource_effect = models.ForeignKey(ResourceEffect)
    properties = models.ManyToManyField(ResourceProperty)
    order = models.PositiveIntegerField()
    is_binary = models.BooleanField()
    actuator_count = models.PositiveIntegerField(
        editable=False, default=0
    )
    read_only = models.BooleanField(default=False, editable=False)

    objects = ActuatorTypeManager()

    def natural_key(self):
        return (self.name, )

    def __str__(self):
        return self.name


class ControlProfileManager(models.Manager):
    def get_by_natural_key(self, actuator_type, name):
        actuator_type = ActuatorType.objects.get_by_natural_key(actuator_type)
        return self.get(actuator_type=actuator_type, name=name)


class ControlProfile(models.Model):
    class Meta:
        unique_together = (('name', 'actuator_type'))

    name = models.CharField(max_length=100)
    actuator_type = models.ForeignKey(
        ActuatorType, related_name='allowed_control_profiles'
    )
    properties = models.ManyToManyField(
        ResourceProperty, through='ActuatorEffect'
    )
    period = models.FloatField()
    pulse_width = models.FloatField()
    read_only = models.BooleanField(default=False, editable=False)

    objects = ControlProfileManager()

    def natural_key(self):
        return (self.actuator_type.name, self.name)
    natural_key.dependencies = ['actuators.ActuatorType']

    def __str__(self):
        return self.name


class ActuatorEffect(models.Model):
    control_profile = models.ForeignKey(ControlProfile, related_name='effects')
    property = models.ForeignKey(ResourceProperty, related_name='+')
    effect_on_active = models.FloatField(default=0)
    threshold = models.FloatField(default=0)


class Actuator(models.Model):
    class Meta:
        unique_together = ('index', 'actuator_type')
        default_related_name = 'actuators'

    index = models.PositiveIntegerField(editable=False)
    name = models.CharField(max_length=100, blank=True)
    actuator_type = models.ForeignKey(ActuatorType)
    control_profile = models.ForeignKey(ControlProfile)
    resource = models.ForeignKey(Resource, related_name='actuators')
    override_value = models.FloatField(editable=False, null=True)
    override_timeout = models.IntegerField(editable=False, null=True)

    def update_override(self):
        if self.override_value and self.override_timeout <= time.time():
            self.override_value = None
            self.override_timeout = None
            self.save()

    def __str__(self):
        return self.name


class ActuatorState(models.Model):
    class Meta:
        ordering = ['timestamp']
        get_latest_by = 'timestamp'

    origin = models.ForeignKey(Actuator, related_name='state+')
    timestamp = models.IntegerField(blank=True, default=time.time)
    value = models.FloatField()
