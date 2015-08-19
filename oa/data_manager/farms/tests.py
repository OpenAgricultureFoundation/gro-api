from slugify import slugify
from django.conf import settings
from django.core.exceptions import ValidationError
from ..data_manager.test import APITestCase, run_with_layouts
from .models import Farm, LayoutChangeAttempted, SlugChangeAttempted
from .cron import UpdateFarmIp

class FarmCRUDTestCase(APITestCase):
    farm_info = {
        'name': 'Test Farm',
        'layout': 'tray',
        'root_server': 'http://cityfarm.media.mit.edu',
    }

    def setUp(self):
        super().setUp()
        self.farm_url = self.url_for_object('farm', 1)

    @run_with_layouts(None)
    def test_farm_creation(self):
        res = self.client.post(self.url_for_object('farm'), self.farm_info)
        self.assertEqual(res.status_code, 405)

    @run_with_layouts(None)
    def test_farm_deletion(self):
        res = self.client.delete(self.farm_url)
        self.assertEqual(res.status_code, 405)

    @run_with_layouts(None)
    def test_slug_generation(self):
        original_name = self.farm_info['name']
        correct_slug = slugify(original_name.lower())
        info_to_send = dict(self.farm_info)
        info_to_send['slug'] = ''
        res = self.client.put(self.farm_url, info_to_send)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['slug'], correct_slug)
        info_to_send = dict(res.data)
        info_to_send['name'] = 'Different Farm'
        res = self.client.put(self.farm_url, info_to_send)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['name'], 'Different Farm')
        self.assertEqual(res.data['slug'], correct_slug)

class FarmLayoutTestCase(APITestCase):
    @run_with_layouts(None)
    def test_layout_locking(self):
        farm_url = self.url_for_object('farm', 1)
        farm_info = {
            'name': 'Test Farm',
            'layout': 'tray',
        }
        res = self.client.get(farm_url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['layout'], None)
        res = self.client.put(farm_url, farm_info)
        self.assertEqual(res.status_code, 200)
        # We shouldn't be able to change the layout
        farm_info['layout'] = 'bay'
        res = self.client.put(farm_url, farm_info)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(
            res.data['detail'], LayoutChangeAttempted.default_detail
        )


class FarmSlugLockingTestCase(APITestCase):
    @run_with_layouts(None)
    def test_slug_locking(self):
        farm_url = self.url_for_object('farm', 1)
        farm_info = {
            'name': 'Test Farm',
            'layout': 'tray',
        }
        res = self.client.get(farm_url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['slug'], None)
        res = self.client.put(farm_url, farm_info)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['slug'], 'test-farm')
        self.assertTrue(res.data['root_id'])
        # We should be able to change the name
        farm_info['name'] = 'Test'
        res = self.client.put(farm_url, farm_info)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['name'], 'Test')
        # We shouldn't be able to change the slug
        farm_info['slug'] = 'new-slug'
        res = self.client.put(farm_url, farm_info)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(
            res.data['detail'], SlugChangeAttempted.default_detail
        )

class UpdateFarmIpTestCase(APITestCase):
    @run_with_layouts(None)
    def test_cron_jon(self):
        farm = Farm.get_solo()
        farm_url = self.url_for_object('farm', 1)
        farm.check_network()
        real_ip = farm.ip
        farm.ip = '12.34.56.78'
        farm.save()
        UpdateFarmIp().do()
        res = self.client.get(farm_url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['ip'], real_ip)
