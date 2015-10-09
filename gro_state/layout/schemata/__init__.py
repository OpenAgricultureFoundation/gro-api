"""
This module encapsulates the set of valid database schemata that can be used to
define the layout of a farm. It allows for the creation of custom database
schemata for custom farm setups by writing a simple configuration file. This
module exports a single variable, "all_schemata", which is a dictionary that
maps all valid schema names to their respective schema dictionaries.

Schema files are written in YAML. Each file must define a ``name`` attribute,
which is a short, preferably one word name of the schema, a
``short_description`` attribute, which a one line description of the schema,
a ``long_description`` which is a full description of the layout, a
``tray_parent`` attribute, which is the name of the parent model for the tray
(defaults to "enclosure"), and an ``entities`` attribute, which is a list of
entities that define a system.

Each entity should have a ``name`` attribute, which is the name of the entity,
a ``description`` attribute, which descriptes what the entity is, and a
``parent`` attribute, which is the name of the parent entity. The ``Tray`` and
``Enclosure`` entities are implied and sit at the bottom and top of the layout
tree, respectively.

For some examples of schema files, see the ``layout/schemata`` directory.
"""

import os
import yaml
import voluptuous
from slugify import slugify

__all__ = [
    'all_schemata', 'Entity', 'Schema', 'register_schema'
]


class Entity:
    schema = voluptuous.Schema({
        voluptuous.Required('name'): str,
        voluptuous.Required('description'): str,
        voluptuous.Required('parents'): [str],
    })

    def __init__(self, **kwargs):
        self.__dict__.update(self.schema(kwargs))


class Schema:
    schema = voluptuous.Schema({
        voluptuous.Required('name'): str,
        voluptuous.Required('short_description'): str,
        voluptuous.Required('long_description'): str,
        voluptuous.Required('entities', default=[]): [Entity.schema],
        voluptuous.Required('tray_parents', default=['Enclosure']): [str],
    })

    def __init__(self, **kwargs):
        # Process keyword arguments
        attrs = self.schema(kwargs)
        entities = attrs.pop('entities')
        tray_parent = attrs.pop('tray_parents')
        self.__dict__.update(attrs)

        # Process supplied entities
        self.entities = {}
        for entity_attrs in entities:
            entity = Entity(**entity_attrs)
            self.entities[entity.name] = entity
        self.generated_entities = dict(self.entities)

        # Create default entities
        self.entities['Tray'] = Entity(
            name='Tray', parents=tray_parent,
            description='A container in which plants are sown'
        )
        self.entities['Enclosure'] = Entity(
            name='Enclosure', parents=[], description='The casing for a farm'
        )

        # Make sure the schema was well-formed
        self.check()

    def check(self):
        # Make sure every entity has at least 1 child and that each entity's
        # parent exists
        entities_without_children = self.entities.copy()
        entities_without_children.pop('Tray')  # Trays shouldn't have children
        for entity in self.entities.values():
            if entity.name == 'Enclosure':
                continue
            for parent in entity.parents:
                if parent == 'Tray':
                    raise voluptuous.SchemaError(
                        'Trays aren\'t allowed to have children'
                    )
                if parent in entities_without_children:
                    entities_without_children.pop(parent)
                if not parent in self.entities:
                    msg = 'Entity "{}" references nonexistant parent "{}"'
                    msg = msg.format(entity.name, parent)
                    raise voluptuous.SchemaError(msg)
        if len(entities_without_children) != 0:
            tmp = ', '.join('"{}"'.format(entity_name) for entity_name in
                            entities_without_children.keys())
            msg = 'The following entities do not have children: {}'.format(tmp)
            raise voluptuous.SchemaError(msg)

all_schemata = {}  # Global registry for loaded schemata

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
    register_schema(Schema(**schema))
