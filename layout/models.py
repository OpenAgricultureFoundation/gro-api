from django.db import models
from django.conf import settings
from model_utils.managers import InheritanceManager
from solo.models import SingletonModel
from cityfarm_api.errors import InvalidNodeType
from farms.models import Farm
from layout.schemata import all_schemata


def schemata_to_use():
    if settings.NODE_TYPE == "LEAF":
        from farms.models import Farm
        farm = Farm.get_solo()
        if farm.is_configured():
            return {farm.layout: all_schemata[farm.layout]}
        else:
            return {}
    elif settings.NODE_TYPE == "ROOT":
        return all_schemata
    else:
        raise InvalidNodeType()


def to_string_method(model_name, model_attr):
    def __str__(self):
        return "{}: {}".format(model_name, getattr(self, model_attr))
    return __str__


#################
# Static Models #
#################

class Model3D(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to="3D_models")
    width = models.FloatField()
    length = models.FloatField()
    height = models.FloatField()
    __str__ = to_string_method("3D Model", "name")


class TrayLayout(models.Model):
    name = models.CharField(max_length=100)
    __str__ = to_string_method("Tray Layout", "name")


class PlantSiteLayout(models.Model):
    parent = models.ForeignKey(TrayLayout, related_name="plant_sites")
    row = models.IntegerField()
    col = models.IntegerField()

    def __str__(self):
        return "{} (r={}, c={})".format(self.parent.name, self.row, self.col)


##########
# Mixins #
##########

class Object3DMixin(models.Model):
    class Meta:
        abstract = True
    model = models.ForeignKey(Model3D, null=True)


class PositionMixin(models.Model):
    class Meta:
        abstract = True
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    z = models.FloatField(default=0)


class SizeMixin(models.Model):
    class Meta:
        abstract = True
    length = models.FloatField(default=0)
    width = models.FloatField(default=0)
    height = models.FloatField(default=0)


def NameMixinFactory(default=None):
    class NameMixin(models.Model):
        class Meta:
            abstract = True
        name = models.CharField(max_length=100, blank=True, default=default)
    return NameMixin


class TrayMixin(models.Model):
    class Meta:
        abstract = True
    num_rows = models.IntegerField(default=0)
    num_cols = models.IntegerField(default=0)
    arrangement = models.ForeignKey(TrayLayout)


def mixins_for_model(model_name, default_name):
    mixins = (NameMixinFactory(default_name), Object3DMixin, SizeMixin)
    if not model_name == "enclosure":
        mixins = mixins + (PositionMixin,)
    if model_name == "tray":
        mixins = mixins + (TrayMixin,)
    return mixins

##################
# Dynamic Models #
##################

all_models = {}
for schema_name, schema in schemata_to_use().items():
    curr_models = {}
    # Create the base LayoutObject model
    model_name = "{}_layout_object".format(schema_name)
    model_attrs = {
        "__module__": __name__,
        "objects": InheritanceManager(),
    }
    LayoutObject = type(model_name, (models.Model,), model_attrs)
    curr_models["layout_object"] = LayoutObject
    layout_object_field = lambda: models.OneToOneField(LayoutObject, parent_link=True)
    # Create the Enclosure model
    model_name = "{}_enclosure".format(schema_name)
    default_name = "{} enclosure".format(Farm.get_solo().name)
    model_classes = mixins_for_model("enclosure", default_name)
    model_attrs = {
        "__module__": __name__,
        "__str__": to_string_method("Enclosure", "name"),
    }
    Enclosure = type(model_name, model_classes, model_attrs)
    curr_models["enclosure"] = Enclosure
    # Create the Tray model
    model_name = "{}_tray".format(schema_name)
    if schema["tray-parent"] == "enclosure":
        default_name = "{} Tray".format(Farm.get_solo().name)
    else:
        default_name = None
    model_classes = (LayoutObject,) + mixins_for_model("tray", default_name)
    model_parent = "{}_{}".format(schema_name, schema["tray-parent"])
    model_attrs = {
        "__module__": __name__,
        "parent": models.ForeignKey(model_parent, related_name="children"),
        "layout_object": layout_object_field(),
        "__str__": to_string_method("Tray", "name"),
    }
    if schema["tray-parent"] == "enclosure":
        model_classes = model_classes + (SingletonModel,)
        model_attrs["parent"].default = 1
    Tray = type(model_name, model_classes, model_attrs)
    curr_models["tray"] = Tray
    # Create the rest of the models
    for entity in schema["entities"]:
        model_name = "{}_{}".format(schema_name, entity["name"])
        if entity["parent"] == "enclosure":
            default_name = "{} {}".format(Farm.get_solo().name, entity["name"])
        else:
            default_name = None
        model_classes = (LayoutObject,) + mixins_for_model(entity["name"],
                                                           default_name)
        model_parent = "{}_{}".format(schema_name, entity["parent"])
        model_attrs = {
            "__module__": __name__,
            "orientation": entity["orientation"],
            "parent": models.ForeignKey(model_parent, related_name="children"),
            "layout_object": layout_object_field(),
            "__str__": to_string_method(entity["name"], "name"),
        }
        if entity["parent"] == "enclosure":
            model_classes = model_classes + (SingletonModel,)
            model_attrs["parent"].default = 1
        CurrModel = type(model_name, model_classes, model_attrs)
        curr_models[entity["name"]] = CurrModel
    all_models[schema_name] = curr_models
