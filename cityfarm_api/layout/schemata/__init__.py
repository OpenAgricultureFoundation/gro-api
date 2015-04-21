"""
This module contains a set of database schemata that can be used to define the
layout of a farm. This allows for the creation of custom database schemata for
custom farm setups. This module exports a single variable, "schemata", this is a
list of database schemata, each of which is represented as a dictionary.
Database schemata are described in yaml files in the directory for this module.
"""
__all__ = ["schemata"]

import os
import yaml
from voluptuous import All, Any, Length, Range, Required, Schema

lower = lambda x: x.lower()
entity = {
    Required('name'): All(str, Length(min=1)),
    Required('type'): All(str, lower, Any("row", "column", "stack")),
    Required('child'): All(str, Length(min=1)),
}
metaschema = Schema({
    Required('name'): All(str, Length(min=1)),
    Required('root'): All(str, Length(min=1)),
    Required('entities', default=[]): [entity],
})

for filename in os.listdir(os.path.dirname(__file__)):
    if not filename.endswith(".yaml"):
        # Only process yaml files
        continue
    file_path = os.path.join(os.path.dirname(__file__), filename)
    with open(file_path, 'r') as schema_file:
        contents = yaml.load(schema_file)
        schema = metaschema(contents)
