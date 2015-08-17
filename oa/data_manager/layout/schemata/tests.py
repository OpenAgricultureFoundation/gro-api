from voluptuous import Invalid, SchemaError
from django.test import TestCase
from layout.schemata import all_schemata, Entity, Schema, register_schema


class InvalidSchemaTestCase(TestCase):
    def test_missing_name(self):
        with self.assertRaises(Invalid):
            Schema({'description': 'Test Schema'})

    def test_missing_description(self):
        with self.assertRaises(Invalid):
            Schema({'name': 'test'})

    def test_invalid_tray_parent(self):
        schema = {
            'name': 'test',
            'description': 'Test Schema',
            'tray-parent': 'test'
        }
        with self.assertRaises(SchemaError):
            Schema(schema)

    def test_entity_with_parent_tray(self):
        schema = {
            'name': 'test',
            'description': 'Test Schema',
            'entities': [{
                'name': 'test',
                'parent': 'tray'
            }],
            'tray-parent': 'enclosure'
        }
        with self.assertRaises(SchemaError):
            Schema(schema)

    def test_entity_with_multiple_children(self):
        schema = {
            'name': 'test',
            'description': 'Test Schema',
            'entities': [
                {
                    'name': 'Test1',
                    'parent': 'Enclosure'
                },
                {
                    'name': 'Test2',
                    'parent': 'Test1',
                },
                {
                    'name': 'Test3',
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
            'description': 'Test Schema',
            'entities': [{
                'name': 'Test',
                'parent': 'FakeParent',
            }],
            'tray-parent': 'Test',
        }
        with self.assertRaises(SchemaError):
            Schema(schema)

    def test_duplicate_name(self):
        schema_attrs = {
            'name': 'test',
            'description': 'Test Schema'
        }
        schema1 = Schema(schema_attrs)
        schema2 = Schema(schema_attrs)
        register_schema(schema1)
        with self.assertRaises(ValueError):
            register_schema(schema2)
