from slugify import slugify
from django.db import models
from django.conf import settings
from solo.models import SingletonModel
from django.db.utils import OperationalError
from model_utils.managers import InheritanceManager

from cityfarm_api.exceptions import InvalidNodeType
from farms.models import Farm
from layout.schemata import all_schemata
from layout.fields import ParentField, ChildrenRelation


def schemata_to_use():
    if settings.NODE_TYPE == "LEAF":
        # On a leaf server, we only need to generate models for the layout the
        # current farm uses
        from farms.models import Farm
        # If the Farm table in the database has not yet been created, we
        # shouldn't generate any models. This is detected by catching an
        # OperationalError
        try:
            farm = Farm.get_solo()
        except OperationalError:
            return {}
        return {farm.layout: all_schemata[farm.layout]} if farm.layout else {}
    elif settings.NODE_TYPE == "ROOT":
        return all_schemata
    else:
        raise InvalidNodeType()


class Model3D(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to="3D_models")
    width = models.FloatField()
    length = models.FloatField()
    height = models.FloatField()
    def __str__(self):
        return self.name


class TrayLayout(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name


class PlantSiteLayout(models.Model):
    parent = models.ForeignKey(TrayLayout, related_name="plant_sites")
    row = models.IntegerField()
    col = models.IntegerField()
    def __str__(self):
        return "(r={}, c={}) in {}".format(self.row, self.col, self.parent.name)

class LayoutObject(models.Model):
    objects = InheritanceManager()

class Enclosure(LayoutObject):
    enclosure_num = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True)
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    z = models.FloatField(default=0)
    length = models.FloatField(default=0)
    width = models.FloatField(default=0)
    height = models.FloatField(default=0)
    model = models.ForeignKey(Model3D, null=True)
    children = ChildrenRelation()

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = "{} Enclosure {}".format(Farm.get_solo().name,
                    self.enclosure_num)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tray(LayoutObject):
    tray_num = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True)
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    z = models.FloatField(default=0)
    length = models.FloatField(default=0)
    width = models.FloatField(default=0)
    height = models.FloatField(default=0)
    model = models.ForeignKey(Model3D, null=True)
    num_rows = models.IntegerField(default=0)
    num_cols = models.IntegerField(default=0)
    arrangement = models.ForeignKey(TrayLayout)
    parent = ParentField()
    children = ChildrenRelation()

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = "{} Tray {}".format(Farm.get_solo().name, self.tray_num)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# A dictionary of all of the classes in the layout tree that have been created
# so we can be sure not to create a class that has already been created
dynamic_models = {}

for schema_name, schema in schemata_to_use().items():
    for entity in schema["entities"]:
        if not entity["name"] in dynamic_models:
            # A model by this name has not been created yet, so create it
            entity_name = entity["name"]
            entity_slug = slugify(entity["name"].lower())
            subid_field = "{}_num".format(entity_slug)
            name_format_string = "{} " + entity_name + " {}"
            def save(self, *args, **kwargs):
                if not self.name:
                    self.name = name_format_string.format(Farm.get_solo().name,
                            getattr(self, subid_field))
                super().save(*args, **kwargs)
            def __str__(self):
                return self.name
            model_attrs = {
                "__module__": __name__,
                subid_field: models.AutoField(primary_key=True),
                "name": models.CharField(max_length=100, blank=True),
                "x": models.FloatField(default=0),
                "y": models.FloatField(default=0),
                "z": models.FloatField(default=0),
                "length": models.FloatField(default=0),
                "width": models.FloatField(default=0),
                "height": models.FloatField(default=0),
                "model": models.ForeignKey(Model3D, null=True),
                "parent": ParentField(),
                "children": ChildrenRelation(),
                "save": save,
                "__str__": __str__,
            }
            Model = type(entity_name, (LayoutObject,), model_attrs)
            dynamic_models[entity_name] = Model

all_models = [Model3D, TrayLayout, PlantSiteLayout, LayoutObject, Enclosure,
        Tray]
all_models = all_models + [model for model_name, model in dynamic_models.items()]
