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
from django.conf import settings
from voluptuous import All, Any, Length, Range, Required, Schema

from cityfarm_api.models import Farm

# Metaschema used to parse the layout schemata in this module
lower = lambda x: x.lower()
entity = {
    Required('name'): All(str, Length(min=1)),
    Required('orientation'): All(str, lower, Any("x", "y", "z")),
    Required('child'): All(str, Length(min=1)),
}
metaschema = Schema({
    Required('name'): All(str, Length(min=1)),
    Required('root'): All(str, Length(min=1)),
    Required('entities', default=[]): [entity],
})

# Function for parsing layout schemata
all_schemata = []
def load_schema_from_file(filename):
    file_path = os.path.join(os.path.dirname(__file__), filename)
    with open(file_path, 'r') as schema_file:
        contents = yaml.load(schema_file)
        schema = metaschema(contents)
        all_schemata[os.path.splitext(filename)[:-1]] = schema

if settings.NODE_TYPE == "ROOT":
    for filename in os.listdir(os.path.dirname(__file__)):
        file_ext = os.path.splitext(filename)[1]
        # Only process yaml files
        if not file_ext == ".yaml":
            continue
        load_schema_from_file(filename)
elif settings.NODE_TYPE == "LEAF":
    farm = Farm.get_solo()
    filename = farm.layout + ".yaml";
    load_schema_from_file(filename)
