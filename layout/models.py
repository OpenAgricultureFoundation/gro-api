from django.db import models
from django.db.utils import OperationalError
from django.db.models.signals import post_save
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.dispatch import receiver
from model_utils.managers import InheritanceManager
from cityfarm_api.utils.state import system_layout
from cityfarm_api.models import Model, SingletonModel, GenerateNameMixin
from cityfarm_api.fields import LayoutForeignKey
from farms.models import Farm
from resources.models import Resource
from .schemata import all_schemata


class Model3D(Model):
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to="3D_models")
    width = models.FloatField()
    length = models.FloatField()
    height = models.FloatField()

    def __str__(self):
        return self.name


class TrayLayout(Model):
    name = models.CharField(max_length=100)
    num_rows = models.IntegerField()
    num_cols = models.IntegerField()

    def __str__(self):
        return self.name


class PlantSiteLayout(Model):
    parent = models.ForeignKey(TrayLayout, related_name="plant_sites")
    row = models.IntegerField()
    col = models.IntegerField()

    def __str__(self):
        return "(r={}, c={}) in {}".format(
            self.row, self.col, self.parent.name
        )


class ParentField(LayoutForeignKey):
    """
    This class is the version of ForeignKey to be used on root servers. It
    can dynamically decide which model it is pointing to based on the
    layout of the farm being viewed.
    """
    def __init__(self, model_name):
        self.model_name = model_name
        kwargs = {'related_name': 'children'}
        super().__init__(**kwargs)

    def get_other_model(self):
        current_layout = system_layout.current_value
        if current_layout is None:
            return None
        schema = all_schemata[current_layout]
        if self.model_name in schema.entities:
            return schema.entities[self.model_name].parent
        else:
            return None

    def deconstruct(self):
        name = self.name
        path = "%s.%s" % (self.__class__.__module__, self.__class__.__name__)
        args = []
        kwargs = {'model_name': self.model_name}
        return name, path, args, kwargs


class Enclosure(GenerateNameMixin, SingletonModel):
    name = models.CharField(max_length=100, blank=True)
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    z = models.FloatField(default=0)
    length = models.FloatField(default=0)
    width = models.FloatField(default=0)
    height = models.FloatField(default=0)
    model = models.ForeignKey(Model3D, null=True, related_name='+')
    resources = GenericRelation(
        Resource, object_id_field='location_id',
        content_type_field='location_type'
    )

    def __str__(self):
        return self.name

@receiver(post_save, sender=Farm)
def create_singleton_instance(sender, instance, **kwargs):
    if instance.name is not None:
        try:
            Enclosure.get_solo()
        except OperationalError:
            pass


class Tray(GenerateNameMixin, Model):
    name = models.CharField(max_length=100, blank=True)
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    z = models.FloatField(default=0)
    length = models.FloatField(default=0)
    width = models.FloatField(default=0)
    height = models.FloatField(default=0)
    model = models.ForeignKey(Model3D, null=True, related_name='+')
    num_rows = models.IntegerField(default=0, editable=False)
    num_cols = models.IntegerField(default=0, editable=False)
    parent = ParentField(model_name='Tray')
    resources = GenericRelation(
        Resource, object_id_field='location_id',
        content_type_field='location_type'
    )

    def __str__(self):
        return self.name


class PlantSite(Model):
    parent = models.ForeignKey(Tray, related_name='plant_sites')
    row = models.IntegerField()
    col = models.IntegerField()

    def __str__(self):
        return '{} (r={}, c={})'.format(str(self.parent), self.row, self.col)


def generate_model_from_entity(entity):
    """
    :param entity: The entity for which to generate a model
    """
    def to_string(self):
        return self.name
    model_attrs = {
        "__module__": __name__,
        "model_name": entity.name,
        "name": models.CharField(max_length=100, blank=True),
        "x": models.FloatField(default=0),
        "y": models.FloatField(default=0),
        "z": models.FloatField(default=0),
        "length": models.FloatField(default=0),
        "width": models.FloatField(default=0),
        "height": models.FloatField(default=0),
        "model": models.ForeignKey(Model3D, null=True, related_name='+'),
        "parent": ParentField(entity.name),
        "resources": GenericRelation(
            Resource, object_id_field='location_id',
            content_type_field='location_type'
        ),
        "__str__": to_string,
    }
    return type(entity.name, (GenerateNameMixin, Model,), model_attrs)

# A dictionary of all of the classes in the layout tree that have been created
# so we can be sure not to create a class that has already been created
dynamic_models = {}

# Generate models for all of the entities that we could encounter
for layout in system_layout.allowed_values:
    for entity in all_schemata[layout].dynamic_entities.values():
        if entity.name not in dynamic_models:
            model = generate_model_from_entity(entity)
            dynamic_models[entity.name] = model
