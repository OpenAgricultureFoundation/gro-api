import time
from django.db import models
from django.db.models.signals import post_migrate
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.fields import GenericRelation
from django.dispatch import receiver
from ..gro_state.models import SingletonModel
from ..farms.models import Farm
from ..resources.models import Resource
from ..recipes.models import RecipeRun
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
    num_rows = models.IntegerField()
    num_cols = models.IntegerField()

    def __str__(self):
        return self.name


class PlantSiteLayout(models.Model):
    parent = models.ForeignKey(TrayLayout, related_name='plant_sites')
    row = models.IntegerField()
    col = models.IntegerField()

    def __str__(self):
        return '(r={}, c={})'.format(self.row, self.col)

class LayoutObject(models.Model):
    name = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=100)
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    z = models.FloatField(default=0)
    length = models.FloatField(default=0)
    width = models.FloatField(default=0)
    height = models.FloatField(default=0)
    model = models.ForeignKey(
        LayoutModel3D, null=True, on_delete=models.SET_NULL, related_name='+'
    )
    parent = models.ForeignKey('self', null=True, related_name='children')

    def __str__(self):
        return self.name

@receiver(post_migrate)
def create_enclosure(sender, **kwargs):
    try:
        LayoutObject.objects.get_or_create(
            pk=1, name='Enclosure', type='Enclosure'
        )
    except OperationalError:
        pass

class EnclosureManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type='Enclosure')

class Enclosure(LayoutObject):
    objects = EnclosureManager()
    class Meta:
        proxy = True

class TrayManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset.filter(type='Tray')

class Tray(LayoutObject):
    objects = TrayManager()
    class Meta:
        proxy = True

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
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return '(r={}, c={})'.format(self.row, self.col)
