from django.conf import settings
from django.utils.functional import cached_property
from solo.models import SingletonModel
from cityfarm_api.utils.state import system_layout
from cityfarm_api.test import (
    APITestCase, run_with_layouts, run_with_all_layouts
)
from .schemata import all_schemata

class UnconfiguredTestCase(APITestCase):
    """
    Make sure none of the layout object types are accessible when the farm has
    not been configured yet
    """
    def test_tray(self):
        tray_url = self.url_for_object('tray')
        self.assertEqual(self.client.get(tray_url).status_code, 403)

    def test_enclosure(self):
        enclosure_url = self.url_for_object('enclosure')
        self.assertEqual(self.client.get(enclosure_url).status_code, 403)

class ObjectCreationMixin:
    @cached_property
    def schema(self):
        return all_schemata[system_layout.current_value]

    def create_object(self, obj_name):
        if obj_name == 'None':
            return
        parent_name = self.schema.entities[obj_name].parent
        self.create_object(parent_name)
        obj_info = {
            'x': 1,
            'y': 1,
            'z': 1,
            'length': 1,
            'width': 1,
            'height': 1,
            'parent': self.url_for_object(parent_name, 1)
        }
        self.client.put(self.url_for_object(obj_name, 1), data=obj_info)

class EnclosureCRUDTestCase(APITestCase):
    @run_with_all_layouts
    def test_enclosure_creation(self):
        enclosure_list_url = self.url_for_object('enclosure')
        res = self.client.get(enclosure_list_url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(self.client.post(enclosure_list_url).status_code, 405)

class AisleCRUDTestCase(APITestCase):
    @run_with_layouts('aisle')
    def test_aisle_creation(self):
        aisle_info = {
            'x': 1,
            'y': 1,
            'z': 1,
            'length': 1,
            'width': 1,
            'height': 1,
            'parent': self.url_for_object('enclosure', 1)
        }
        res = self.client.post(self.url_for_object('aisle'), data=aisle_info)
        self.assertEqual(res.status_code, 201)
        res = self.client.get(self.url_for_object('aisle'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

class BayCRUDTestCase(APITestCase, ObjectCreationMixin):
    @run_with_layouts('aisle', 'bay')
    def test_bay_creation(self):
        bay_parent = self.schema.entities['Bay'].parent
        self.create_object(bay_parent)
        bay_info = {
            'x': 1,
            'y': 1,
            'z': 1,
            'length': 1,
            'width': 1,
            'height': 1,
            'parent': self.url_for_object(bay_parent, 1)
        }
        res = self.client.post(self.url_for_object('bay'), data=bay_info)
        self.assertEqual(res.status_code, 201)
        res = self.client.get(self.url_for_object('bay'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

class TrayCRUDTestCase(APITestCase, ObjectCreationMixin):
    @run_with_all_layouts
    def test_tray_creation(self):
        tray_parent = self.schema.entities['Tray'].parent
        self.create_object(tray_parent)
        tray_info = {
            'x': 1,
            'y': 1,
            'z': 1,
            'length': 1,
            'width': 1,
            'height': 1,
            'parent': self.url_for_object(tray_parent, 1)
        }
        res = self.client.post(self.url_for_object('tray'), data=tray_info)
        self.assertEqual(res.status_code, 201)
        res = self.client.get(self.url_for_object('tray'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
