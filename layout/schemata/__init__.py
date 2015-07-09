"""
This module encapsulates the set of valid database schemata that can be used to
define the layout of a farm. It allows for the creation of custom database
schemata for custom farm setups by writing a simple configuration file. This
module exports a single variable, "all_schemata", which is a dictionary that
maps all valid schema names to their respective schema dictionaries.

Schema files are written in YAML. Each file must define a ``name`` attribute,
which is a short, preferably one word name of the schema, a ``description``
attribute, which a one line description of the schema, a ``tray-parent``
attribute, which is the name of the parent model for the trays (defaults to
"enclosure"), and an ``entities`` attribute, which is a list of entities that
define a system.

Each entity should have a ``name`` attribute, which is the name of the entity,
and a ``parent`` attribute, which is the name of the parent entity. The ``Tray``
and ``Enclosure`` entities are implied and sit at the bottom and top of the
layout tree, respectively.

For some examples of schema files, see the ``layout/schemata`` directory.
"""

import os
import copy
import yaml
import voluptuous
from slugify import slugify

__all__ = [
    'all_schemata', 'Entity', 'Schema', 'register_schema'
]

def to_slug(string):
    """
    Clean the name of a layout object by making it lowercase and slugifying it.
    """
    return slugify(str(string))

class Entity:
    schema = voluptuous.Schema({
        voluptuous.Required('name'): to_slug,
        voluptuous.Required('parent'): to_slug,
    })
    def __init__(self, attrs=None, **kwargs):
        all_attrs = dict(attrs) if attrs else {}
        all_attrs.update(kwargs)
        all_attrs = self.schema(all_attrs)
        self.name = all_attrs['name']
        self.parent = all_attrs['parent']

class Schema:
    schema = voluptuous.Schema({
        voluptuous.Required('name'): str,
        voluptuous.Required('description'): str,
        voluptuous.Required('entities', default=[]): [Entity.schema],
        voluptuous.Required('tray-parent', default='Enclosure'): to_slug,
    })
    def __init__(self, attrs=None, **kwargs):
        all_attrs = attrs.copy()
        all_attrs.update(kwargs)
        all_attrs = self.schema(all_attrs)
        self.name = all_attrs['name']
        self.description = all_attrs['description']
        self.entities = {}
        for entity_attrs in all_attrs['entities']:
            entity = Entity(entity_attrs)
            self.entities[entity.name] = entity
        self.dynamic_entities = copy.deepcopy(self.entities)
        self.entities['Tray'] = Entity(
            name='Tray', parent=all_attrs['tray-parent']
        )
        self.entities['Enclosure'] = Entity(name='Enclosure', parent=None)
        for entity in self.entities.values():
            if hasattr(self, entity.name):
                raise RuntimeError(
                    'Schema {} contained an entity with invalid name {}'.format(
                        self.name, entity.name
                    )
                )
            setattr(self, entity.name, entity)
        self.check()

    def check(self):
        entities_without_children = self.entities.copy() # A dictionary of all
        # of the entities without children. It is initialized to the full set of
        # entities and should be emptied by the end of this function
        entities_without_children.pop('Tray')  # Trays shouldn't have children
        # Maps the name of an entity to the name of that entity's child
        entity_children = {}
        for entity in self.entities.values():
            if entity.name == 'Enclosure':
                continue
            if entity.parent == 'Tray':
                raise voluptuous.SchemaError(
                    'Trays aren\'t allowed to have children'
                )
            elif entity.parent in entities_without_children:
                entities_without_children.pop(entity.parent)
                entity_children[entity.parent] = entity.name
            else:
                if entity.parent in entity_children:
                    msg = 'Entity "{}" has multiple children: "{}" and "{}"'
                    msg = msg.format(
                        entity.parent, entity_children[entity.parent],
                        entity.name
                    )
                    raise voluptuous.SchemaError(msg)
                else:
                    msg = 'Entity "{}" references nonexistant parent "{}"'
                    msg = msg.format(entity.name, entity.parent)
                    raise voluptuous.SchemaError(msg)
        # In practice, this can never happen, but we check it anyway to be safe
        if len(entities_without_children) != 0:
            tmp = ', '.join('"{}"'.format(entity_name) for entity_name in
                            entities_without_children.keys())
            msg = 'The following entities do not have children: {}'.format(tmp)
            raise voluptuous.SchemaError(msg)

all_schemata = {} # Global registry for loaded schemata

def register_schema(schema):
    if schema.name in all_schemata:
        raise ValueError(
            "Tried to register a schema named '%s', but a schema by that name "
            "has already been registered" % schema.name
        )
    all_schemata[schema.name] = schema

# Load all of the schema files from this directory
for filename in os.listdir(os.path.dirname(__file__)):
    file_ext = os.path.splitext(filename)[1]
    # Only process yaml files
    if not file_ext == '.yaml':
        continue
    file_path = os.path.join(os.path.dirname(__file__), filename)
    with open(file_path, 'r') as schema_file:
        schema = yaml.load(schema_file)
    register_schema(Schema(schema))
