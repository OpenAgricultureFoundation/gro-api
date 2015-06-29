from slugify import slugify
from django.db import models
from django.conf import settings
from solo.models import SingletonModel
from django.db.utils import OperationalError
from django.utils.functional import cached_property
from model_utils.managers import InheritanceManager

from cityfarm_api.state import StateVariable
from cityfarm_api.models import DynamicModelBase
from cityfarm_api.fields import (
    state_dependent_cached_property, dynamic_foreign_key
)
from farms.models import Farm
from layout.schemata import all_schemata

def schemata_to_use():
    if settings.SERVER_TYPE == settings.LEAF:
        # On a leaf server, we only need to generate models for the layout the
        # current farm uses
        # If the Farm table in the database has not yet been created, we
        # shouldn't generate any dynamic models. This is detected by catching an
        # OperationalError.
        try:
            farm = Farm.get_solo()
        except OperationalError:
            return {}
        return {farm.layout: all_schemata[farm.layout]} if farm.layout else {}
    if settings.SERVER_TYPE == settings.ROOT:
        return all_schemata

class LayoutVariable(StateVariable):
    def current_value(self):
        return Farm.get_solo().layout
    def allowed_values(self):
        return schemata_to_use().keys()

class LayoutModelBase(DynamicModelBase):
    state_var = LayoutVariable()

class LayoutModel(models.Model, metaclass=LayoutModelBase):
    class Meta:
        abstract = True

per_layout_cached_property = state_dependent_cached_property(LayoutVariable())
LayoutForeignKey = dynamic_foreign_key(LayoutVariable())

class ParentField(LayoutForeignKey):
    def to_for_state(self, state):
        layout = state
        model_name = self.opts.model_name
        if model_name == 'tray':
            return all_schemata[layout].tray.parent
        else:
            return getattr(all_schemata[layout], self.opts.model_name).parent

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


class LayoutObject(LayoutModel):
    objects = InheritanceManager()

    def save(self, *args, **kwargs):
        # Generate pk to include in default name
        super().save(*args, **kwargs)
        if not self.name:
            self.name = "{} {} {}".format(
                Farm.get_solo().name,
                self.model_name,
                self.pk
            )
        # save() is not idempotent with force_insert=True
        if 'force_insert' in kwargs and kwargs['force_insert']:
            kwargs['force_insert'] = False
        return super().save(*args, **kwargs)

class Enclosure(LayoutObject, SingletonModel):
    enclosure_num = models.AutoField(primary_key=True)
    layout_object = models.OneToOneField(
        LayoutObject, parent_link=True, editable=False
    )
    name = models.CharField(max_length=100, blank=True)
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    z = models.FloatField(default=0)
    length = models.FloatField(default=0)
    width = models.FloatField(default=0)
    height = models.FloatField(default=0)
    model = models.ForeignKey(Model3D, null=True)

    def __str__(self):
        return self.name


class Tray(LayoutObject):
    tray_num = models.AutoField(primary_key=True)
    layout_object = models.OneToOneField(
        LayoutObject, parent_link=True, editable=False
    )
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
    parent = ParentField()

    def __str__(self):
        return self.name

# A dictionary of all of the classes in the layout tree that have been created
# so we can be sure not to create a class that has already been created
dynamic_models = {}

for schema_name, schema in schemata_to_use().items():
    for entity in schema.dynamic_entities.values():
        entity_slug = slugify(entity.name.lower())
        if entity_slug not in dynamic_models:
            # A model by this name has not been created yet, so create it
            subid_field = "{}_num".format(entity_slug)
            name_format_string = "{} " + entity.name + " {}"

            def __str__(self):
                return getattr(self, 'name', '%s object' % self.model_name)
                return self.name or '%s object' % self.model_name
            model_attrs = {
                "__module__": __name__,
                "model_name": entity.name,
                subid_field: models.AutoField(primary_key=True),
                "layout_object": models.OneToOneField(
                    LayoutObject, parent_link=True, editable=False
                ),
                "name": models.CharField(max_length=100, blank=True),
                "x": models.FloatField(default=0),
                "y": models.FloatField(default=0),
                "z": models.FloatField(default=0),
                "length": models.FloatField(default=0),
                "width": models.FloatField(default=0),
                "height": models.FloatField(default=0),
                "model": models.ForeignKey(Model3D, null=True),
                "parent": ParentField(),
                "__str__": __str__,
            }
            Model = type(entity_slug, (LayoutObject,), model_attrs)
            dynamic_models[entity_slug] = Model
