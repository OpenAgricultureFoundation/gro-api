from slugify import slugify
from rest_framework.test import APITestCase
from django.conf import settings
from django.core.exceptions import ValidationError
from farms.models import Farm, LayoutChangeAttempted

URL_PREFIX = '' if settings.SERVER_TYPE == settings.LEAF else '/tray'
LIST_URL = URL_PREFIX + '/farm/'
FARM_URL = URL_PREFIX + '/farm/1/'
EXAMPLE_FARM_INFO = {
    'name': 'Test Farm',
    'slug': 'test-farm',
    'root_server': 'http://cityfarm.media.mit.edu',
    'ip': '12.34.56.78',
    'layout': 'aisle',
}

class FarmTestCase(APITestCase):
    def test_farm_creation(self):
        res = self.client.post(LIST_URL)
        self.assertEqual(res.status_code, 405)

    def test_field_editing(self):
        Farm.get_solo()  # Make sure the singleton has been created
        res = self.client.put(FARM_URL, data=EXAMPLE_FARM_INFO)
        self.assertEqual(res.status_code, 200)
        for required_field in ['name', 'layout']:
            info_to_send = dict(EXAMPLE_FARM_INFO)
            info_to_send.pop(required_field)
            res = self.client.put(FARM_URL, data=info_to_send)
            self.assertEqual(res.status_code, 400)
            self.assertEqual(
                res.data[required_field][0], 'This field is required.'
            )
        for non_required_field in ['slug', 'root_server']:
            info_to_send = dict(EXAMPLE_FARM_INFO)
            info_to_send.pop(non_required_field)
            res = self.client.put(FARM_URL, data=info_to_send)
            self.assertEqual(res.status_code, 200)
        res = self.client.get(FARM_URL)
        self.assertEqual(res.status_code, 200)
        farm_state = res.data
        for read_only_field in ['root_id', 'ip']:
            old_value = farm_state[read_only_field]
            info_to_send = dict(EXAMPLE_FARM_INFO)
            info_to_send[read_only_field] = 'test value'
            res = self.client.put(FARM_URL, data=info_to_send)
            self.assertEqual(res.data[read_only_field], old_value)

    def test_farm_deletion(self):
        Farm.get_solo()  # Make sure the singleton has been created
        res = self.client.delete(FARM_URL)
        self.assertEqual(res.status_code, 405)

    def test_slug_generation(self):
        Farm.get_solo()  # Make sure the singleton has been created
        original_name = EXAMPLE_FARM_INFO['name']
        correct_slug = slugify(original_name.lower())
        info_to_send = dict(EXAMPLE_FARM_INFO)
        info_to_send['slug'] = ''
        res = self.client.put(FARM_URL, info_to_send)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['slug'], correct_slug)
        info_to_send = dict(res.data)
        info_to_send['name'] = 'Different Farm'
        res = self.client.put(FARM_URL, info_to_send)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['name'], 'Different Farm')
        self.assertEqual(res.data['slug'], correct_slug)

class FarmLayoutTestCase(APITestCase):
    # This test requires an initially unconfigured farm, so we separate it into
    # a separate test case to ensure that it is run on a fresh database
    def test_layout_locking(self):
        Farm.get_solo()  # Make sure the singleton has been created
        res = self.client.get(FARM_URL)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['layout'], None)
        res = self.client.put(FARM_URL, data=EXAMPLE_FARM_INFO)
        self.assertEqual(res.status_code, 200)
        farm_info = dict(EXAMPLE_FARM_INFO)
        farm_info['layout'] = 'bay'
        res = self.client.put(FARM_URL, data=farm_info)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(
            res.data['detail'], LayoutChangeAttempted.default_detail
        )
