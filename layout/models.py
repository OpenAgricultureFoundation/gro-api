from django.db import models
from solo.models import SingletonModel
from model_utils.managers import InheritanceManager
from cityfarm_api.utils import get_current_layout
from cityfarm_api.state import StateVariable
from cityfarm_api.errors import FarmNotConfiguredError
from cityfarm_api.fields import (
    state_dependent_cached_property, dynamic_foreign_key
)
from farms.models import Farm
from .utils import schemata_to_use
from .schemata import all_schemata

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

class LayoutVariable(StateVariable):
    @classmethod
    def current_value(_=None):
        return get_current_layout()
    @classmethod
    def allowed_values(_=None):
        return schemata_to_use().keys()

per_layout_cached_property = state_dependent_cached_property(LayoutVariable())
LayoutForeignKey = dynamic_foreign_key(LayoutVariable())

class ParentField(LayoutForeignKey):
    def __init__(self, *args, **kwargs):
        self.model_name = kwargs.pop('model_name', None)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['model_name'] = self.model_name
        return name, path, args, kwargs

    def contribute_to_class(self, cls, name, virtual_only=False):
        self.model_name = cls.__name__
        super().contribute_to_class(cls, name, virtual_only=virtual_only)

    def to_for_state(self, state):
        if self.model_name:
            return getattr(all_schemata[state], self.model_name).parent
        else:
            return None


class LayoutObject(models.Model):
    objects = InheritanceManager()

    def save(self, *args, **kwargs):
        # Generate pk to include in default name
        res = super().save(*args, **kwargs)
        if self._meta.get_field('name') and not self.name:
            farm = Farm.get_solo()
            self.name = "{} {} {}".format(
                Farm.get_solo().name,
                self.__class__.__name__,
                self.pk
            )
            # save() is not idempotent with force_insert=True
            if 'force_insert' in kwargs and kwargs['force_insert']:
                kwargs['force_insert'] = False
            res = super().save(*args, **kwargs)
        return res

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
        if entity.name not in dynamic_models:
            # A model by this name has not been created yet, so create it
            subid_field = "{}_num".format(entity.name)
            name_format_string = "{} " + entity.name + " {}"

            def __str__(self):
                return self.name
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
            Model = type(entity.name, (LayoutObject,), model_attrs)
            dynamic_models[entity.mname] = Model
