from django.conf import settings
from django.utils.functional import cached_property
from solo.models import SingletonModel
from ..data_manager.utils import system_layout
from ..data_manager.test import (
    APITestCase, run_with_layouts, run_with_all_layouts
)
from .schemata import all_schemata

class UnconfiguredTestCase(APITestCase):
    @run_with_layouts(None)
    def test_tray(self):
        tray_url = self.url_for_object('tray')
        self.assertEqual(self.client.get(tray_url).status_code, 403)

    @run_with_layouts(None)
    def test_enclosure(self):
        enclosure_url = self.url_for_object('enclosure')
        self.assertEqual(self.client.get(enclosure_url).status_code, 403)


generic_obj_info = {
    'x': 1,
    'y': 1,
    'z': 1,
    'length': 1,
    'width': 1,
    'height': 1,
}


class EnclosureCRUDTestCase(APITestCase):
    @run_with_all_layouts
    def test_enclosure_creation(self):
        enclosure_list_url = self.url_for_object('enclosure')
        res = self.client.get(enclosure_list_url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(self.client.post(enclosure_list_url).status_code, 405)

class AisleCRUDTestCase(APITestCase):
    @run_with_layouts('aisle')
    def test_aisle_creation(self):
        aisle_info = dict(generic_obj_info)
        aisle_info['parent'] = self.url_for_object('enclosure', 1)
        res = self.client.post(self.url_for_object('aisle'), aisle_info)
        self.assertEqual(res.status_code, 201)
        res = self.client.get(self.url_for_object('aisle'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data['results']), 1)


class BayCRUDTestCase(APITestCase):
    @run_with_layouts('aisle')
    def test_bay_creation_given_aisle(self):
        aisle_info = dict(generic_obj_info)
        aisle_info['parent'] = self.url_for_object('enclosure', 1)
        res = self.client.post(self.url_for_object('aisle'), aisle_info)
        self.assertEqual(res.status_code, 201)
        aisle_url = res.data['url']
        self.test_bay_creation_given_bay(aisle_url)

    @run_with_layouts('bay')
    def test_bay_creation_given_bay(self, parent=None):
        parent_url = parent or self.url_for_object('enclosure', 1)
        bay_info  = dict(generic_obj_info)
        bay_info['parent'] = parent_url
        res = self.client.post(self.url_for_object('bay'), bay_info)
        self.assertEqual(res.status_code, 201)
        res = self.client.get(self.url_for_object('bay'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data['results']), 1)


class TrayCRUDTestCase(APITestCase):
    @run_with_layouts('aisle')
    def test_tray_creation_given_aisle(self):
        aisle_info = dict(generic_obj_info)
        aisle_info['parent'] = self.url_for_object('enclosure', 1)
        res = self.client.post(self.url_for_object('aisle'), aisle_info)
        self.assertEqual(res.status_code, 201)
        aisle_url = res.data['url']
        self.test_tray_creation_given_bay(aisle_url)

    @run_with_layouts('bay')
    def test_tray_creation_given_bay(self, parent=None):
        parent_url = parent or self.url_for_object('enclosure', 1)
        bay_info  = dict(generic_obj_info)
        bay_info['parent'] = parent_url
        res = self.client.post(self.url_for_object('bay'), bay_info)
        self.assertEqual(res.status_code, 201)
        bay_url = res.data['url']
        self.test_tray_creation_given_tray(bay_url)

    @run_with_layouts('tray')
    def test_tray_creation_given_tray(self, parent=None):
        parent_url = parent or self.url_for_object('enclosure', 1)
        tray_info  = dict(generic_obj_info)
        tray_info['parent'] = parent_url
        res = self.client.post(self.url_for_object('tray'), tray_info)
        self.assertEqual(res.status_code, 201)
        res = self.client.get(self.url_for_object('tray'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data['results']), 1)
