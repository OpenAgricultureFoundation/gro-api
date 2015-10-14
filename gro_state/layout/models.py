import time
from django.db import models
from django.db.models.signals import (
    post_migrate, pre_save, post_save, pre_delete, post_delete
)
from django.core.exceptions import ObjectDoesNotExist
from django.dispatch import receiver
from ..core.const import ENCLOSURE, TRAY
from ..farms.models import Farm
from .schemata import all_schemata


class LayoutModel3D(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    file = models.FileField(upload_to='3D_models')
    width = models.FloatField()
    length = models.FloatField()
    height = models.FloatField()

    def __str__(self):
        return self.name


class TrayLayout(models.Model):
    name = models.CharField(max_length=100)
    num_rows = models.IntegerField(editable=False)
    num_cols = models.IntegerField(editable=False)
    is_locked = models.BooleanField(default=False)

    def __str__(self):
        return self.name

@receiver(pre_delete, sender=TrayLayout)
def protect_locked_instances(sender, instance, **kwargs):
    if instance.is_locked:
        raise models.ProtectedError('Deleting locked tray layouts is not allowed')


class PlantSiteLayout(models.Model):
    parent = models.ForeignKey(TrayLayout, related_name='plant_sites')
    row = models.IntegerField()
    col = models.IntegerField()

    def __str__(self):
        return '(r={}, c={})'.format(self.row, self.col)

@receiver(post_save, sender=PlantSiteLayout)
def increase_tray_layout_dimensions(sender, instance, **kwargs):
    if instance.row >= instance.parent.num_rows:
        instance.parent.num_rows = instance.row + 1
        instance.parent.save()
    if instance.col >= instance.parent.num_cols:
        instance.parent.num_cols = instance.col + 1
        instance.parent.save()

@receiver(pre_delete, sender=PlantSiteLayout)
def protect_if_parent_is_locked(sender, instance, **kwargs):
    if instance.parent.is_locked:
        raise ProtectedError(
            'Deleting the plant sites from locked tray layouts is not allowed'
        )

@receiver(post_delete, sender=PlantSiteLayout)
def decrease_tray_layout_dimensions(sender, instance, **kwargs):
    max_row = max(x.row for x in instance.parent.plant_sites.all())
    max_col = max(x.col for x in instance.parent.plant_sites.all())
    instance.parent.num_rows = max_row + 1
    instance.parent.num_cols = mac_col + 1
    instance.parent.save()


class LayoutObject(models.Model):
    name = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    z = models.FloatField(default=0)
    outer_length = models.FloatField(default=0)
    outer_width = models.FloatField(default=0)
    outer_height = models.FloatField(default=0)
    offset_x = models.FloatField(default=0)
    offset_y = models.FloatField(default=0)
    offset_z = models.FloatField(default=0)
    inner_length = models.FloatField(default=0)
    inner_width = models.FloatField(default=0)
    inner_height = models.FloatField(default=0)
    model = models.ForeignKey(
        LayoutModel3D, null=True, on_delete=models.PROTECT,
        related_name='in_use_by'
    )
    parent = models.ForeignKey('self', null=True, related_name='children')

    def __str__(self):
        return self.name

@receiver(pre_save, sender=LayoutObject)
def name_layout_object(sender, instance, **kwargs):
    if not instance.name:
        instance.name = "{} {}".format(
            instance.type,
            LayoutObject.objects.filter(type=instance.type).count() + 1
        )

@receiver(post_migrate)
def create_enclosure(sender, **kwargs):
    try:
        LayoutObject.objects.get_or_create(
            pk=1, name=ENCLOSURE, type=ENCLOSURE
        )
    except OperationalError:
        pass


class EnclosureManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=ENCLOSURE)

class Enclosure(LayoutObject):
    objects = EnclosureManager()
    class Meta:
        proxy = True


class TrayManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset.filter(type=TRAY)

class Tray(LayoutObject):
    objects = TrayManager()
    class Meta:
        proxy = True


class TrayInfo(models.Model):
    tray = models.OneToOneField(Tray, related_name='extra_info')
    num_rows = models.IntegerField()
    num_cols = models.IntegerField()


class TrayLayoutHistory(models.Model):
    class Meta:
        ordering = ['start_timestamp']
        get_latest_by = 'start_timestamp'
    tray = models.ForeignKey(Tray, related_name='+')
    layout = models.ForeignKey(TrayLayout, related_name='+')
    start_timestamp = models.IntegerField()
    end_timestamp = models.IntegerField(null=True)


def generate_manager_from_type(obj_type):
    manager_name = '{}Manager'.format(obj_type)
    def get_queryset(self, obj_type=obj_type):
        return super().get_queryset.filter(type=obj_type)
    return type(
        manager_name, (models.Manager,), {'get_queryset': get_queryset}
    )

def generate_model_from_entity(entity):
    class Meta:
        proxy = True
    attrs = {
        '__module__': __name__,
        'objects': generate_manager_from_type(entity.name)(),
        'Meta': Meta,
    }
    return type(entity.name, (LayoutObject,), attrs)

# Generate models for all of the entities that we could encounter
generated_models = {}
for schema in all_schemata.values():
    for entity in schema.generated_entities.values():
        if entity.name not in generated_models:
            model = generate_model_from_entity(entity)
            generated_models[entity.name] = model


class PlantSite(models.Model):
    parent = models.ForeignKey(LayoutObject, related_name='plant_sites')
    row = models.IntegerField()
    col = models.IntegerField()
    is_active = models.BooleanField()

    def __str__(self):
        return '(r={}, c={})'.format(self.row, self.col)
