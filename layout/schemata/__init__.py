"""
This module contains a set of database schemata that can be used to define the
layout of a farm. This allows for the creation of custom database schemata for
custom farm setups. This module exports a single variable, "all_schemata", which
is a list of relevant database schemata, each of which is represented as a
dictionary. In a LEAF node of the API, only the schema for the node's layout
will be included in the list. In a ROOT node of the API, all schema will be
included.
"""
# TODO: describe the format of the yaml files

__all__ = ["all_schemata"]

import os
import yaml
from cityfarm_api.errors import InvalidNodeType
from django.conf import settings
from django.db.utils import OperationalError
from voluptuous import All, Any, Length, Range, Required, Schema

# Metaschema used to parse the layout schemata in this module
lower = lambda x: x.lower()
entity = {
    Required('name'): All(str, lower),
    Required('orientation'): All(str, lower, Any("x", "y", "z")),
    Required('parent'): All(str, lower),
}
metaschema = Schema({
    Required('name'): All(str, lower),
    Required('entities', default=[]): [entity],
    Required('tray-parent', default="enclosure"): All(str, lower),
})

all_schemata = {}
def validate_schema(schema):
    # Make sure each parent actually exists
    entities = schema["entities"]
    entity_names = [entity["name"] for entity in entities] + ["enclosure"]
    for entity in entities:
        assert entity["parent"] in entity_names, "Entity %s references " + \
            "nonexistant parent %s" % (entity["name"], entity["parent"])
    assert schema["tray-parent"] in entity_names, "Tray has nonexistant " + \
        "parent %s" % schema["tray-parent"]

def load_schema_from_file(filename):
    file_path = os.path.join(os.path.dirname(__file__), filename)
    with open(file_path, 'r') as schema_file:
        contents = yaml.load(schema_file)
        schema = metaschema(contents)
        validate_schema(schema)
        all_schemata[os.path.splitext(filename)[0]] = schema

for filename in os.listdir(os.path.dirname(__file__)):
    file_ext = os.path.splitext(filename)[1]
    # Only process yaml files
    if not file_ext == ".yaml":
        continue
    load_schema_from_file(filename)

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
