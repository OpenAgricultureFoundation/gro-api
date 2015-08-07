from cityfarm_api.test import APITestCase, run_with_any_layout
from cityfarm_api.serializers import model_serializers
from resources.models import ResourceType
from .models import ActuatorType, Actuator

class ActuatorTypeTestCase(APITestCase):
    @run_with_any_layout
    def test_visible_fields(self):
        ActuatorTypeSerializer = model_serializers.get_for_model(ActuatorType)
        fields = ActuatorTypeSerializer().get_fields()
        fields.pop('url')
        fields.pop('code')
        fields.pop('name')
        fields.pop('resource_type')
        fields.pop('properties')
        fields.pop('order')
        fields.pop('is_binary')
        fields.pop('effect_on_active')
        fields.pop('read_only')
        fields.pop('actuator_creation_count')
        fields.pop('actuators')
        self.assertFalse(fields)

    @run_with_any_layout
    def test_edit_stock_type(self):
        water_id = ResourceType.objects.get_by_natural_key('W').pk
        data = {
            'code': 'TS',
            'name': 'test',
            'resource_type': self.url_for_object('resourceType', water_id),
            'properties': [],
            'order': 0,
            'is_binary': True,
            'effect_on_active': 1,
        }
        heater_id = ActuatorType.objects.get_by_natural_key('A', 'HE').pk
        res = self.client.put(
            self.url_for_object('actuatorType', heater_id), data=data
        )
        self.assertEqual(res.status_code, 403)

    @run_with_any_layout
    def test_edit_custom_type(self):
        water_id = ResourceType.objects.get_by_natural_key('W').pk
        data = {
            'code': 'TS',
            'name': 'test',
            'resource_type': self.url_for_object('resourceType', water_id),
            'properties': [],
            'order': 0,
            'is_binary': True,
            'effect_on_active': 1,
        }
        res = self.client.post(self.url_for_object('actuatorType'), data=data)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['name'], 'test')
        data['name'] = 'test2'
        res = self.client.put(res.data['url'], data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['name'], 'test2')

    @run_with_any_layout
    def test_invalid_code(self):
        water_id = ResourceType.objects.get_by_natural_key('W').pk
        data = {
            'code': 'T',
            'name': 'test',
            'resource_type': self.url_for_object('resourceType', water_id),
            'properties': [],
            'order': 0,
            'is_binary': True,
            'effect_on_active': 1,
        }
        res = self.client.post(self.url_for_object('actuatorType'), data=data)
        self.assertEqual(res.status_code, 400)
        data['code'] = 'TES'
        res = self.client.post(self.url_for_object('actuatorType'), data=data)
        self.assertEqual(res.status_code, 400)
