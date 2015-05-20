from django.db import models, OperationalError
from django.conf import settings
from model_utils.managers import InheritanceManager
from solo.models import SingletonModel
from cityfarm_api.errors import InvalidNodeType
from layout.schemata import all_schemata

def schemata_to_use():
    if settings.NODE_TYPE == "LEAF":
        from farms.models import Farm
        try:
            farm = Farm.get_solo()
        except OperationalError as e:
            return {}
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

class Model3D(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to="3D_models")
    width = models.FloatField()
    length = models.FloatField()
    height = models.FloatField()
    __str__ = to_string_method("3D Model", "name")

class Object3D(models.Model):
    class Meta:
        abstract = True
    model = models.ForeignKey(Model3D, null=True)

class Enclosure(SingletonModel):
    class Meta:
        abstract = True
    length = models.FloatField(null=True)
    width = models.FloatField(null=True)
    height = models.FloatField(null=True)

class LocationMixin(models.Model):
    class Meta:
        abstract = True
    length = models.FloatField(null=True)
    width = models.FloatField(null=True)
    height = models.FloatField(null=True)
    x = models.FloatField(null=True)
    y = models.FloatField(null=True)
    z = models.FloatField(null=True)


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
    # Create the Enclosure model
    enclosure_name = "{}_enclosure".format(schema_name)
    enclosure_classes = (Enclosure, Object3D)
    enclosure_attrs = {
        "__module__": __name__,
        "__str__": to_string_method("Enclosure", "id"),
    }
    Enclosure = type(enclosure_name, enclosure_classes, enclosure_attrs)
    curr_models["enclosure"] = Enclosure
    # Create the Tray model
    tray_name = "{}_tray".format(schema_name)
    tray_classes = (LayoutObject, LocationMixin, Object3D)
    tray_parent = "{}_{}".format(schema_name, schema["tray-parent"])
    tray_attrs = {
        "__module__": __name__,
        "num_rows": models.IntegerField(null=True),
        "num_cols": models.IntegerField(null=True),
        "parent": models.ForeignKey(tray_parent, related_name="children"),
        "layout_object": models.OneToOneField(LayoutObject, parent_link=True),
        "__str__": to_string_method("Tray", "id"),
    }
    if schema["tray-parent"] == "enclosure":
        tray_classes = tray_classes + (SingletonModel,)
        tray_attrs["parent"].default = 1
    Tray = type(tray_name, tray_classes, tray_attrs)
    curr_models["tray"] = Tray
    # Create the rest of the models
    for entity in schema["entities"]:
        model_name = "{}_{}".format(schema_name, entity["name"])
        model_classes = (LayoutObject, LocationMixin, Object3D)
        model_parent = "{}_{}".format(schema_name, entity["parent"])
        model_attrs = {
            "__module__": __name__,
            "orientation": entity["orientation"],
            "parent": models.ForeignKey(model_parent, related_name="children"),
            "layout_object": models.OneToOneField(LayoutObject, parent_link=True),
            "__str__": to_string_method(entity["name"], "id"),
        }
        if entity["parent"] == "enclosure":
            model_classes = model_classes + (SingletonModel,)
            model_attrs["parent"].default = 1
        CurrModel = type(model_name, model_classes, model_attrs)
        curr_models[entity["name"]] = CurrModel
    all_models[schema_name] = curr_models
