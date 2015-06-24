"""
This module encapsulates the set of valid database schemata that can be used to
define the layout of a farm. It allows for the creation of custom database
schemata for custom farm setups by writing a simple configuration file. This
module exports a single variable, "all_schemata", which is a dictionary that
maps all valid schema names to their respective schema dictionaries.

Schema files are written in YAML. Each file must define a ``name`` attribute,
which is the name of the schema, a ``tray-parent`` attribute, which is the name
of the parent model for the trays (defaults to "enclosure"), and an ``entities``
attribute, which is a list of entities that define a system.

Each entity should have a ``name`` attribute, which is the name of the entity,
and a ``parent`` attribute, which is the name of the parent entity. The ``Tray``
and ``Enclosure`` entities are implied and sit at the bottom and top of the
layout tree, respectively.

For some examples of schema files, see the ``layout/schemata`` directory.
"""

import os
import yaml
from slugify import slugify
from voluptuous import Required, Schema, SchemaError

__all__ = ['all_schemata']
all_schemata = {}  # Global registry for loaded schemata


def to_slug(string):
    """
    Clean the name of a layout object by making it lowercase and slugifying it.
    """
    return slugify(str(string).lower())

# Metaschema used to parse the layout schemata in this module
ENTITY = {
    Required('name'): to_slug,
    Required('parent'): to_slug,
}
METASCHEMA = Schema({
    Required('name'): str,
    Required('entities', default=[]): [ENTITY],
    Required('tray-parent', default='enclosure'): to_slug,
})


def validate_schema(schema):
    """
    Make sure that the passed-in schema is valid
    """
    # A dictionary that maps entity names to entity dictionaries
    entities = {entity['name']: entity for entity in schema['entities']}
    entities['tray'] = {
        'parent': schema['tray-parent'],
    }
    entities['enclosure'] = {}
    # A dictionary of all of the entities without children. It is initialized to
    # the full set of entities and should be emptied by the end of this function
    entities_without_children = entities.copy()
    entities_without_children.pop('tray')  # Trays shouldn't have children
    # Maps the name of an entity to the name of that entity's child
    entity_children = {}
    for entity_name, entity in entities.items():
        if entity_name == 'enclosure':
            continue
        entity_parent = entity['parent']
        if entity_parent == 'tray':
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
    """
    Interpret the dictionary ``schema`` as a schema named ``schema_name``,
    validate it,  and save it in the ``all_schemata`` dictionary.
    """
    if schema_name in all_schemata:
        msg = 'A schema by the name {} has already been loaded'
        msg = msg.format(schema_name)
        raise ValueError(msg)
    schema = METASCHEMA(schema)
    validate_schema(schema)

    # Reform schema to simplify lookups
    entities = schema['entities']
    entities = {entity['name']: entity for entity in entities}
    schema['entities'] = entities

    all_schemata[schema_name] = schema
    return schema


def load_schema_from_file(schema_filename):
    """
    Load the schema from the file with the given filename.
    """
    schema_name = os.path.splitext(schema_filename)[0]
    file_path = os.path.join(os.path.dirname(__file__), schema_filename)
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
