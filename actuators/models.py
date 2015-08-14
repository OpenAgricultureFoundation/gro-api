import time
from django.db import models
from django.db.utils import OperationalError
from resources.models import ResourceType, ResourceProperty, Resource


class ActuatorClassManager(models.Manager):
    def get_by_natural_key(self, type_code, class_code):
        resource_type = ResourceType.objects.get_by_natural_key(type_code)
        return self.get(resource_type=resource_type, code=class_code)


class ActuatorClass(models.Model):
    class Meta:
        unique_together = (
            ('code', 'resource_type'), ('name', 'resource_type')
        )
        default_related_name = 'actuator_classes'

    code = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=100, unique=True)
    resource_type = models.ForeignKey(ResourceType)

    objects = ActuatorClassManager()

    def natural_key(self):
        return (self.resource_type.code, self.code)

    def __str__(self):
        return self.name


class ActuatorType(models.Model):
    class Meta:
        default_related_name = 'actuator_types'

    name = models.CharField(max_length=100)
    actuator_class = models.ForeignKey(ActuatorClass)
    properties = models.ManyToManyField(ResourceProperty)
    order = models.PositiveIntegerField()
    is_binary = models.BooleanField()
    actuator_count = models.PositiveIntegerField(
        editable=False, default=0
    )

    def __str__(self):
        return self.name


class ControlProfile(models.Model):
    name = models.CharField(max_length=100)
    actuator_type = models.ForeignKey(
        ActuatorType, related_name='allowed_control_profiles'
    )
    properties = models.ManyToManyField(
        ResourceProperty, through='ActuatorEffect'
    )
    period = models.FloatField()
    pulse_width = models.FloatField()

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
    timestamp = models.IntegerField()
    value = models.FloatField()
