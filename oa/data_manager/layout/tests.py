from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.functional import cached_property
from solo.models import SingletonModel
from ..data_manager.utils import system_layout
from ..data_manager.test import (
    APITestCase, run_with_layouts, run_with_all_layouts
)
from .schemata import all_schemata

class LayoutAuthMixin:
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            'layout', 'layout@test.com', 'layout'
        )
        layout_editors_group = Group.objects.get(name='LayoutEditors')
        cls.user.groups.add(layout_editors_group)

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        self.client.force_authenticate()


generic_obj_info = {
    'x': 0,
    'y': 0,
    'z': 0,
    'length': 1,
    'width': 1,
    'height': 1,
}


class EnclosureCRUDTestCase(LayoutAuthMixin, APITestCase):
    @run_with_all_layouts
    def test_enclosure_creation(self):
        enclosure_list_url = self.url_for_object('enclosure')
        res = self.client.get(enclosure_list_url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(self.client.post(enclosure_list_url).status_code, 403)

class AisleCRUDTestCase(LayoutAuthMixin, APITestCase):
    @run_with_layouts('aisle')
    def test_aisle_creation(self):
        aisle_info = dict(generic_obj_info)
        aisle_info['parent'] = self.url_for_object('enclosure', 1)
        res = self.client.post(self.url_for_object('aisle'), aisle_info)
        self.assertEqual(res.status_code, 201)
        res = self.client.get(self.url_for_object('aisle'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data['results']), 1)


class BayCRUDTestCase(LayoutAuthMixin, APITestCase):
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


class TrayCRUDTestCase(LayoutAuthMixin, APITestCase):
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
