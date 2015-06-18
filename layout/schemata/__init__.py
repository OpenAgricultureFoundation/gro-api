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
import copy
import yaml
from slugify import slugify
from functools import wraps
from voluptuous import Required, Schema, SchemaError, Invalid

__all__ = ['all_schemata']
all_schemata = {}  # Global registry for loaded schemata


# Metaschema used to parse the layout schemata in this module
entity = {
    Required('name'): str,
    Required('parent'): str,
}
metaschema = Schema({
    Required('name'): str,
    Required('entities', default=[]): [entity],
    Required('tray-parent', default='Enclosure'): str,
})


def validate_schema(schema):
    # A dictionary that maps entity names to entity dictionaries
    entities = {entity['name']: entity for entity in schema['entities']}
    entities['Tray'] = {
        'parent': schema['tray-parent'],
    }
    entities['Enclosure'] = {}
    # A dictionary of all of the entities without children. It is initialized to
    # the full set of entities and should be emptied by the end of this function
    entities_without_children = entities.copy()
    entities_without_children.pop('Tray')  # Trays shouldn't have children
    # Maps the name of an entity to the name of that entity's child
    entity_children = {}
    for entity_name, entity in entities.items():
        if entity_name == 'Enclosure':
            continue
        entity_parent = entity['parent']
        if entity_parent == 'Tray':
            raise SchemaError('Trays aren\'t allowed to have children')
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
        tmp = ', '.join('"{}"'.format(entity_name) for entity_name in
                        entities_without_children.keys())
        msg = 'The following entities do not have children: {}'.format(tmp)
        raise SchemaError(msg)


def load_schema_from_dict(schema_name, schema):
    if schema_name in all_schemata:
        msg = 'A schema by the name {} has already been loaded'
        msg = msg.format(schema_name)
        raise ValueError(msg)
    schema = metaschema(schema)
    validate_schema(schema)
    # Reform schema to simplify lookups
    entities = schema['entities']
    entities = {slugify(entity['name'].lower()): entity for entity in entities}
    schema['entities'] = entities
    all_schemata[schema_name] = schema
    return schema


def load_schema_from_file(filename):
    schema_name = os.path.splitext(filename)[0]
    file_path = os.path.join(os.path.dirname(__file__), filename)
    with open(file_path, 'r') as schema_file:
        schema = yaml.load(schema_file)
    return load_schema_from_dict(schema_name, schema)

# Load all of the schema files from this directory
for filename in os.listdir(os.path.dirname(__file__)):
    file_ext = os.path.splitext(filename)[1]
    # Only process yaml files
    if not file_ext == '.yaml':
        continue
    load_schema_from_file(filename)
