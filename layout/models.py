"""
This module defines the Django models that describe the layout of a farm. A
model is generated for every possible layout object name. Only the ones used for
the current farm layout are marked as managed in a leaf server. In a root
server, none of the models are managed.
"""
from django.apps import apps
from django.db import connections, models
from django.db.models import ForeignKey, PositiveIntegerField
from django.db.models.signals import pre_migrate
from django.conf import settings
from solo.models import SingletonModel
from cityfarm_api.utils import get_current_layout
from cityfarm_api.state import StateVariable
from cityfarm_api.models import Model
from cityfarm_api.fields import (
    state_dependent_cached_property, dynamic_foreign_key
)
from farms.models import Farm
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
        return "(r={}, c={}) in {}".format(self.row, self.col, self.parent.name)

if settings.SERVER_TYPE == settings.LEAF:
    def parent_field_for_model(model_name):
        curr_schema = all_schemata[get_current_layout()]
        if model_name in curr_schema.entities:
            return ForeignKey(
                curr_schema.entities[model_name].parent, related_name="children"
            )
        else:
            return PositiveIntegerField()
else:
    class LayoutVariable(StateVariable):
        """
        This state variable represents the layout of the current farm. The current
        value is read from the singleton farm instance. In a leaf server, the only
        allowed value is the current one because the server is restarted whenever
        the farm layout is changed. In a leaf server, all farm layouts are allowed.
        """
        @staticmethod
        def current_value():
            return get_current_layout()
        @staticmethod
        def allowed_values():
            if settings.SERVER_TYPE == settings.LEAF:
                return get_current_layout()
            else:
                return all_schemata.keys()

    per_layout_cached_property = state_dependent_cached_property(LayoutVariable())
    LayoutForeignKey = dynamic_foreign_key(LayoutVariable())

    class ParentField(LayoutForeignKey):
        """
        This class is the version of ForeignKey to be used on root servers. It
        can dynamically decide which model it is pointing to based on the layout
        of the farm being viewed.
        """
        def __init__(self, *args, **kwargs):
            kwargs.pop('model')
            self.model_name = kwargs.pop('model_name', None)
            kwargs['related_name'] = 'children'
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

    def parent_field_for_model(model_name):
        return ParentField(model_name=model_name)

class LayoutObject(Model):
    class Meta(Model.Meta):
        abstract = True

    def save(self, *args, **kwargs):
        # pylint: disable=access-member-before-definition
        # Generate pk to include in default name
        res = super().save(*args, **kwargs)
        if self._meta.get_field('name') and not self.name:
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
    name = models.CharField(max_length=100, blank=True)
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    z = models.FloatField(default=0)
    length = models.FloatField(default=0)
    width = models.FloatField(default=0)
    height = models.FloatField(default=0)
    model = models.ForeignKey(Model3D, null=True, related_name='+')

    def __str__(self):
        return self.name

class Tray(LayoutObject):
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
    parent = parent_field_for_model('Tray')

    def __str__(self):
        return self.name

class PlantSite(Model):
    parent = models.ForeignKey(Tray, related_name='plant_sites')
    row = models.IntegerField()
    col = models.IntegerField()
    def __str__(self):
        return '{} (r={}, c={})'.format(str(self.parent), self.row, self.col)

# A dictionary of all of the classes in the layout tree that have been created
# so we can be sure not to create a class that has already been created
dynamic_models = {}

def generate_model_from_entity(entity, managed):
    """
    :param entity: The entity for which to generate a model
    :param bool managed: Whether or not the returned model should be managed
    """
    _managed = managed # Scoping is weird
    class Meta:
        managed = _managed
    def __str__(self):
        return self.name
    model_attrs = {
        "__module__": __name__,
        "Meta": Meta,
        "model_name": entity.name,
        "name": models.CharField(max_length=100, blank=True),
        "x": models.FloatField(default=0),
        "y": models.FloatField(default=0),
        "z": models.FloatField(default=0),
        "length": models.FloatField(default=0),
        "width": models.FloatField(default=0),
        "height": models.FloatField(default=0),
        "model": models.ForeignKey(Model3D, null=True, related_name='+'),
        "parent": parent_field_for_model(entity.name),
        "__str__": __str__,
    }
    return type(entity.name, (LayoutObject,), model_attrs)

if settings.SERVER_TYPE == settings.LEAF:
    # Generate managed models for all entities in the schema for the current
    # layout
    schema = all_schemata[get_current_layout()]
    for entity in schema.dynamic_entities.values():
        model = generate_model_from_entity(entity, True)
        dynamic_models[entity.name] = model
        # When we switch models from unmanaged to managed, we break some of the
        # migration logic because Django expects the model to have a table in
        # the database already, and that might not be true. Thus, we listen for
        # a pre_migration signal and create an empty table for this model if it
        # hasn't already been created.
        def create_table(sender, app_config, verbosity, interactive, using,
                         model=model, **kwargs):
            with connections[using].schema_editor() as schema_editor:
                try:
                    schema_editor.create_model(model)
                except:
                    # Lets try to finish the migration anyway. This might just
                    # mean that the table already exists
                    pass
        sender = apps.get_app_config(model._meta.app_label)
        uid = 'create_table_for_%s' % entity.name.lower()
        pre_migrate.connect(
            create_table, sender=sender, weak=False, dispatch_uid=uid
        )
# Generate unmanaged models for all other entities
for schema_name, schema in all_schemata.items():
    for entity in schema.dynamic_entities.values():
        if not entity.name in dynamic_models:
            dynamic_models[entity.name] = generate_model_from_entity(entity, False)
