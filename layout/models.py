from slugify import slugify
from django.db import models
from django.conf import settings
from solo.models import SingletonModel
from django.db.utils import OperationalError
from django.utils.functional import cached_property
from model_utils.managers import InheritanceManager

from farms.models import Farm
from layout.schemata import all_schemata
from layout.fields import (
    per_layout_cached_property, DynamicForeignKey, DynamicRelation
)


class ParentField(DynamicForeignKey):
    @per_layout_cached_property
    def available_models(self):
        models = dynamic_models.copy()
        models.update({
            'enclosure': Enclosure
        })
        return models

    @per_layout_cached_property
    def related_model(self):
        farm_layout = Farm.get_solo().layout
        layout_schema = all_schemata[farm_layout]
        if self.model_name == 'tray':
            parent_name = layout_schema['tray-parent']
        else:
            parent_name = layout_schema['entities'][self.model_name]['parent']
        parent_name = slugify(parent_name.lower())
        return self.available_models[parent_name]


class ChildrenRelation(DynamicRelation):
    remote_field_name = 'parent'

    @per_layout_cached_property
    def available_models(self):
        models = dynamic_models.copy()
        models.update({
            'tray': Tray,
        })
        return models

    @per_layout_cached_property
    def related_model(self):
        farm_layout = Farm.get_solo().layout
        layout_schema = all_schemata[farm_layout]
        if slugify(layout_schema['tray-parent'].lower()) == self.model_name:
            child_name = 'Tray'
        else:
            for entity_name, entity in layout_schema['entities'].items():
                parent_name = slugify(entity['parent'].lower())
                if parent_name == self.model_name:
                    child_name = entity_name
                    break
        child_name = slugify(child_name.lower())
        return self.available_models[child_name]

def schemata_to_use():
    if settings.SERVER_TYPE == settings.LEAF:
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
    if settings.SERVER_TYPE == settings.ROOT:
        return all_schemata


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
    model_name = "Enclosure"
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
    children = ChildrenRelation()

    def __str__(self):
        return self.name


class Tray(LayoutObject):
    model_name = "Tray"
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
    for entity in schema['entities'].values():
        entity_name = entity["name"]
        entity_slug = slugify(entity_name.lower())
        if entity_slug not in dynamic_models:
            # A model by this name has not been created yet, so create it
            subid_field = "{}_num".format(entity_slug)
            name_format_string = "{} " + entity_name + " {}"

            def __str__(self):
                return getattr(self, 'name', '%s object' % self.model_name)
                return self.name or '%s object' % self.model_name
            model_attrs = {
                "__module__": __name__,
                "model_name": entity_name,
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
                "children": ChildrenRelation(),
                "__str__": __str__,
            }
            Model = type(entity_slug, (LayoutObject,), model_attrs)
            dynamic_models[entity_slug] = Model
