from cityfarm_api.test import APITestCase, run_with_any_layout
from cityfarm_api.serializers import model_serializers
from resources.models import ResourceType, ResourceProperty
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
        fields.pop('actuator_count')
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

    @run_with_any_layout
    def test_invalid_properties(self):
        water_id = ResourceType.objects.get_by_natural_key('W').pk
        air_temp_id = ResourceProperty.objects.get_by_natural_key('A', 'TM').pk
        data = {
            'code': 'TS',
            'name': 'test',
            'resource_type': self.url_for_object('resourceType', water_id),
            'properties': [
                self.url_for_object('resourceProperty', air_temp_id)
            ],
            'order': 0,
            'is_binary': True,
            'effect_on_active': 1,
        }
        res = self.client.post(self.url_for_object('actuatorType'), data=data)
        self.assertEqual(res.status_code, 400)


class ActuatorTestCase(APITestCase):
    @run_with_any_layout
    def test_visible_fields(self):
        ActuatorSerializer = model_serializers.get_for_model(Actuator)
        fields = ActuatorSerializer().get_fields()
        fields.pop('url')
        fields.pop('index')
        fields.pop('name')
        fields.pop('actuator_type')
        fields.pop('resource')
        fields.pop('override_value')
        fields.pop('override_timeout')
        self.assertFalse(fields)

    @run_with_any_layout
    def test_actuator_creation(self):
        # Create a resource to install the actuator in
        air_id = ResourceType.objects.get_by_natural_key('A').pk
        resource_info = {
            'resource_type': self.url_for_object('resourceType', air_id),
            'location': self.url_for_object('enclosure', 1)
        }
        res = self.client.post(
            self.url_for_object('resource'), data=resource_info
        )
        self.assertEqual(res.status_code, 201)
        resource = res.data
        # Create the actuator
        heater_id = ActuatorType.objects.get_by_natural_key('A', 'HE').pk
        actuator_info = {
            'actuator_type': self.url_for_object('actuatorType', heater_id),
            'resource': resource['url'],
        }
        res = self.client.post(
            self.url_for_object('actuator'), data=actuator_info
        )
        self.assertEqual(res.status_code, 201)
        actuator = res.data
        # Validate the index and name
        res = self.client.get(actuator['actuator_type'])
        self.assertEqual(res.status_code, 200)
        actuator_type = res.data
        num_actuators = actuator_type['actuator_count']
        self.assertEqual(actuator['index'], num_actuators)
        expected_name = "{} Instance {}".format(
            actuator_type['name'], num_actuators
        )
        self.assertEqual(actuator['name'], expected_name)
        # Change the name
        actuator_info['name'] = 'test'
        res = self.client.put(actuator['url'], data=actuator_info)
        self.assertEqual(res.status_code, 200)
        actuator = res.data
        self.assertEqual(actuator['name'], 'test')
        # Try changing the type
        old_actuator_type_url = actuator['actuator_type']
        circulation_id = ActuatorType.objects.get_by_natural_key('A', 'CR').pk
        actuator_info['actuator_type'] = self.url_for_object(
            'actuatorType', circulation_id
        )
        res = self.client.put(actuator['url'], data=actuator_info)
        self.assertEqual(res.status_code, 400)
        actuator_info['actuator_type'] = old_actuator_type_url
        # Create a new resource of a different type
        water_id = ResourceType.objects.get_by_natural_key('W').pk
        new_resource_info = {
            'resource_type': self.url_for_object('resourceType', water_id),
            'location': self.url_for_object('enclosure', 1)
        }
        res = self.client.post(
            self.url_for_object('resource'), data=new_resource_info
        )
        self.assertEqual(res.status_code, 201)
        new_resource = res.data
        # Try to move the actuator to the new resource
        actuator_info['resource'] = new_resource['url']
        res = self.client.put(actuator['url'], data=actuator_info)
        self.assertEqual(res.status_code, 400)

class ActuatorStateTestCase(APITestCase):
    # TODO: Test state routes
    pass
