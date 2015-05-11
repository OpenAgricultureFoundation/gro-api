"""
This module encapsulates the set of valid database schemata that can be used to
define the layout of a farm. It allows for the creation of custom database
schemata for custom farm setups by writing a simple configuration file. This
module exports a single variable, "all_schemata", which is a dictionary that
maps all valid schema names to their respective schema dictionaries.

Schema files are written in YAML...
"""
# TODO: describe the format of the yaml files

import os
import yaml
from functools import wraps
from voluptuous import All, In, Required, Schema, SchemaError, Lower, Invalid

__all__ = ["all_schemata"]
all_schemata = {}  # Global registry for loaded schemata


# Define a voluptuous validator for disallowing certain reserved words in the
# schema
class NotInInvalid(Invalid):
    pass


def NotIn(container, msg=None):
    """Validate that a value is not in a collection."""
    @wraps(NotIn)
    def validator(value):
        if value in container:
            raise NotInInvalid(msg or 'value is not allowed')
        return value
    return validator

# Metaschema used to parse the layout schemata in this module
# TODO: Add the entity names from all other apps to this list
RESERVED_ENTITY_NAMES = ["tray", "enclosure"]
entity = {
    Required('name'): All(Lower, NotIn(RESERVED_ENTITY_NAMES)),
    Required('orientation'): All(Lower, In(["x", "y", "z"])),
    Required('parent'): Lower,
}
metaschema = Schema({
    Required('name'): Lower,
    Required('entities', default=[]): [entity],
    Required('tray-parent', default="enclosure"): Lower,
})


def validate_schema(schema):
    # A dictionary that maps entity names to entity dictionaries
    entities = {entity["name"]: entity for entity in schema["entities"]}
    entities["tray"] = {
        "parent": schema["tray-parent"],
    }
    entities["enclosure"] = {}
    # A dictionary of all of the entities without children. It is initialized to
    # the full set of entities and should be emptied by the end of this function
    entities_without_children = entities.copy()
    entities_without_children.pop("tray")  # Trays shouldn't have children
    # Maps the name of an entity to the name of that entity's child
    entity_children = {}
    for entity_name, entity in entities.items():
        if entity_name == "enclosure":
            continue
        entity_parent = entity["parent"]
        if entity_parent == "tray":
            raise SchemaError("Trays aren't allowed to have children")
        elif entity_parent in entities_without_children:
            entities_without_children.pop(entity_parent)
            entity_children[entity_parent] = entity_name
        else:
            if entity_parent in entity_children:
                msg = 'Entity "{}" has multiple children: "{}" and "{}"'
                msg = msg.format(entity_parent, entity_children[entity_parent],
                                 entity_name)
                raise SchemaError(msg)
            else:
                msg = 'Entity "{}" references nonexistant parent "{}"'
                msg = msg.format(entity_name, entity_parent)
                raise SchemaError(msg)
    # In practice, this can never happen, but we check it anyway to be safe
    if len(entities_without_children) != 0:
        tmp = ", ".join('"{}"'.format(entity_name) for entity_name in
                        entities_without_children.keys())
        msg = 'The following entities do not have children: {}'.format(tmp)
        raise SchemaError(msg)


def load_schema_from_dict(schema_name, schema):
    if schema_name in all_schemata:
        msg = "A schema by the name {} has already been loaded"
        msg = msg.format(schema_name)
        raise ValueError(msg)
    schema = metaschema(schema)
    validate_schema(schema)
    all_schemata[schema_name] = schema
    return schema


def load_schema_from_file(filename):
    schema_name = os.path.splitext(filename)[0]
    file_path = os.path.join(os.path.dirname(__file__), filename)
    with open(file_path, 'r') as schema_file:
        schema = yaml.load(schema_file)
    return load_schema_from_dict(schema_name, schema)

for filename in os.listdir(os.path.dirname(__file__)):
    file_ext = os.path.splitext(filename)[1]
    # Only process yaml files
    if not file_ext == ".yaml":
        continue
    load_schema_from_file(filename)
