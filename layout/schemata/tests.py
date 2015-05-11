from voluptuous import Invalid
from django.test import TestCase
from layout.schemata import load_schema_from_dict, SchemaError


class InvalidSchemaTestCase(TestCase):
    def test_missing_name(self):
        schema = {}
        with self.assertRaises(Invalid):
            load_schema_from_dict("test", schema)

    def test_duplicate_name(self):
        schema1 = {"name": "test"}
        schema2 = schema1.copy()
        load_schema_from_dict("test_duplicate", schema1)
        with self.assertRaises(ValueError):
            load_schema_from_dict("test_duplicate", schema2)

    def test_invalid_tray_parent(self):
        schema = {"name": "test", "tray-parent": "test"}
        with self.assertRaises(SchemaError):
            load_schema_from_dict("test", schema)

    def test_invalid_entity_name(self):
        entity = {"name": "tray", "orientation": "x", "parent": "enclosure"}
        schema = {"name": "test", "entities": [entity], "tray-parent": "tray"}
        with self.assertRaises(Invalid):
            load_schema_from_dict("test", schema)

    def test_invalid_entity_orientation(self):
        entity = {"name": "test", "orientation": "q", "parent": "enclosure"}
        schema = {"name": "test", "entities": [entity], "tray-parent": "test"}
        with self.assertRaises(Invalid):
            load_schema_from_dict("test", schema)

    def test_entity_with_parent_tray(self):
        entity = {"name": "test", "orientation": "x", "parent": "tray"}
        schema = {"name": "test", "entities": [entity]}
        with self.assertRaises(SchemaError):
            load_schema_from_dict("test", schema)

    def test_entity_with_multiple_children(self):
        entity1 = {"name": "test1", "orientation": "x", "parent": "enclosure"}
        entity2 = {"name": "test2", "orientation": "x", "parent": "test1"}
        entity3 = {"name": "test3", "orientation": "x", "parent": "test1"}
        schema = {"name": "test", "entities": [entity1, entity2, entity3],
                  "tray-parent": "test2"}
        with self.assertRaises(SchemaError):
            load_schema_from_dict("test", schema)

    def test_entity_with_nonexistant_parent(self):
        entity = {"name": "test", "orientation": "x", "parent": "parent"}
        schema = {"name": "test", "entities": [entity], "tray-parent": "test"}
        with self.assertRaises(SchemaError):
            load_schema_from_dict("test", schema)
