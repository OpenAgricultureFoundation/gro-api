from django.db import models
from django.conf import settings
from layout.schemata import schemata_to_use
from solo.models import SingletonModel
from cityfarm_api.errors import InvalidNodeType

class DimensionsMixin(models.Model):
    width = models.FloatField(null=True)
    length = models.FloatField(null=True)
    height = models.FloatField(null=True)
    class Meta:
        abstract = True

class CoordinatesMixin(models.Model):
    x = models.FloatField(null=True)
    y = models.FloatField(null=True)
    z = models.FloatField(null=True)
    class Meta:
        abstract = True

def create_model(name, base_class=models.Model, fields={}):
    return type(name, (base_class,), fields)

all_models = {}
for schema_name, schema in schemata_to_use().items():
    curr_models = {}
    # Create the Enclosure model
    enclosure_name = "{}_enclosure".format(schema_name)
    enclosure_classes = (SingletonModel, DimensionsMixin)
    enclosure_attrs = {
        "__module__": __name__,
    }
    Enclosure = type(enclosure_name, enclosure_classes, enclosure_attrs)
    curr_models["enclosure"] = Enclosure
    # Create the Tray model
    tray_name = "{}_tray".format(schema_name)
    tray_classes = (DimensionsMixin, CoordinatesMixin)
    tray_parent = "{}_{}".format(schema_name, schema["tray-parent"])
    tray_attrs = {
        "__module__": __name__,
        "num_rows": models.IntegerField(),
        "num_cols": models.IntegerField(),
        "parent": models.ForeignKey(tray_parent, related_name="children"),
    }
    Tray = type(tray_name, tray_classes, tray_attrs)
    curr_models["tray"] = Tray
    # Create the rest of the models
    for entity in schema["entities"]:
        model_name = "{}_{}".format(schema_name, entity["name"])
        model_classes = (DimensionsMixin, CoordinatesMixin)
        model_parent = "{}_{}".format(schema_name, entity["parent"])
        model_attrs = {
            "__module__": __name__,
            "orientation": entity["orientation"],
            "parent": models.ForeignKey(model_parent, related_name="children"),
        }
        if entity["parent"] == "enclosure":
            model_classes = model_classes + (SingletonModel,)
            model_attrs["parent"].default = 1
        CurrModel = type(model_name, model_classes, model_attrs)
        curr_models[entity["name"]] = CurrModel
    all_models[schema_name] = curr_models
