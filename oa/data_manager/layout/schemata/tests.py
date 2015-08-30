from voluptuous import Invalid, SchemaError
from django.test import TestCase
from . import all_schemata, Entity, Schema, register_schema


class InvalidSchemaTestCase(TestCase):
    def test_missing_name(self):
        with self.assertRaises(Invalid):
            Schema({
                'short_description': 'Test Schema',
                'long_description': 'A schema for testing',
            })

    def test_missing_short_description(self):
        with self.assertRaises(Invalid):
            Schema({
                'name': 'test',
                'long_description': 'Test Schema',
            })

    def test_missing_long_description(self):
        with self.assertRaises(Invalid):
            Schema({
                'name': 'test',
                'short_description': 'Test Schema',
            })

    def test_invalid_tray_parent(self):
        schema = {
            'name': 'test',
            'short_description': 'Test Schema',
            'long_description': 'Test Schema',
            'tray-parent': 'test'
        }
        with self.assertRaises(SchemaError):
            Schema(schema)

    def test_entity_with_parent_tray(self):
        schema = {
            'name': 'test',
            'short_description': 'Test Schema',
            'long_description': 'A schema for testing',
            'entities': [{
                'name': 'test',
                'description': 'An entity for testing',
                'parent': 'tray'
            }],
            'tray-parent': 'enclosure'
        }
        with self.assertRaises(SchemaError):
            Schema(schema)

    def test_entity_with_multiple_children(self):
        schema = {
            'name': 'test',
            'short_description': 'Test Schema',
            'long_description': 'A schema for testing',
            'entities': [
                {
                    'name': 'Test1',
                    'description': 'An entity for testing',
                    'parent': 'Enclosure'
                },
                {
                    'name': 'Test2',
                    'description': 'An entity for testing',
                    'parent': 'Test1',
                },
                {
                    'name': 'Test3',
                    'description': 'An entity for testing',
                    'parent': 'Test1',
                },
            ],
            'tray-parent': 'Test1',
        }
        with self.assertRaises(SchemaError):
            Schema(schema)

    def test_entity_with_nonexistant_parent(self):
        schema = {
            'name': 'test',
            'short_description': 'Test Schema',
            'long_description': 'A schema for testing',
            'entities': [{
                'name': 'Test',
                'description': 'An entity for testing',
                'parent': 'FakeParent',
            }],
            'tray-parent': 'Test',
        }
        with self.assertRaises(SchemaError):
            Schema(schema)

    def test_duplicate_name(self):
        schema_attrs = {
            'name': 'test',
            'short_description': 'Test Schema',
            'long_description': 'Test Schema'
        }
        schema1 = Schema(schema_attrs)
        schema2 = Schema(schema_attrs)
        register_schema(schema1)
        with self.assertRaises(ValueError):
            register_schema(schema2)
