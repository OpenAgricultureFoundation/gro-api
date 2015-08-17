from slugify import slugify
from django.conf import settings
from django.core.exceptions import ValidationError
from cityfarm_api.test import APITestCase
from farms.models import Farm, LayoutChangeAttempted
from .cron import UpdateFarmIp

class FarmCRUDTestCase(APITestCase):
    farm_info = {
        'name': 'Test Farm',
        'slug': 'test-farm',
        'layout': 'tray',
        'root_server': 'http://cityfarm.media.mit.edu',
    }

    def setUp(self):
        super().setUp()
        self.farm_url = self.url_for_object('farm', 1)

    def test_farm_creation(self):
        res = self.client.post(self.farm_url)
        self.assertEqual(res.status_code, 405)

    def test_field_editing(self):
        res = self.client.put(self.farm_url, data=self.farm_info)
        self.assertEqual(res.status_code, 200)
        for required_field in ['name', 'layout']:
            info_to_send = dict(self.farm_info)
            info_to_send.pop(required_field)
            res = self.client.put(self.farm_url, data=info_to_send)
            self.assertEqual(res.status_code, 400)
            self.assertEqual(
                res.data[required_field][0], 'This field is required.'
            )
            self.assertEqual(len(res.data[required_field]), 1)
        for non_required_field in ['slug', 'root_server']:
            info_to_send = dict(self.farm_info)
            info_to_send.pop(non_required_field)
            res = self.client.put(self.farm_url, data=info_to_send)
            self.assertEqual(res.status_code, 200)
        res = self.client.get(self.farm_url)
        self.assertEqual(res.status_code, 200)
        farm_state = res.data
        for read_only_field in ['root_id', 'ip']:
            old_value = farm_state[read_only_field]
            info_to_send = dict(self.farm_info)
            info_to_send[read_only_field] = 'test value'
            res = self.client.put(self.farm_url, data=info_to_send)
            self.assertEqual(res.data[read_only_field], old_value)

    def test_farm_deletion(self):
        res = self.client.delete(self.farm_url)
        self.assertEqual(res.status_code, 405)

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
    def test_layout_locking(self):
        farm_url = self.url_for_object('farm', 1)
        farm_info = {
            'name': 'Test Farm',
            'layout': 'tray',
        }
        res = self.client.get(farm_url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['layout'], None)
        res = self.client.put(farm_url, data=farm_info)
        self.assertEqual(res.status_code, 200)
        farm_info['layout'] = 'bay'
        res = self.client.put(farm_url, data=farm_info)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(
            res.data['detail'], LayoutChangeAttempted.default_detail
        )

class UpdateFarmIpTestCase(APITestCase):
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
