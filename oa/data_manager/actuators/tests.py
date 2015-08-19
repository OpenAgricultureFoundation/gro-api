from ..data_manager.test import APITestCase, run_with_any_layout
from ..resources.models import ResourceType, ResourceProperty, ResourceEffect
from .models import ActuatorType, ControlProfile, Actuator
from .serializers import ActuatorTypeSerializer, ActuatorSerializer

class ActuatorTypeTestCase(APITestCase):
    @run_with_any_layout
    def test_visible_fields(self):
        fields = ActuatorTypeSerializer().get_fields()
        fields.pop('url')
        fields.pop('name')
        fields.pop('resource_effect')
        fields.pop('properties')
        fields.pop('order')
        fields.pop('is_binary')
        fields.pop('actuator_count')
        fields.pop('read_only')
        fields.pop('actuators')
        fields.pop('allowed_control_profiles')
        self.assertFalse(fields)

    @run_with_any_layout
    def test_edit_stock_type(self):
        heater_id = ResourceEffect.objects.get_by_natural_key('A', 'HE').pk
        data = {
            'name': 'test',
            'resource_effect': self.url_for_object('resourceEffect', heater_id),
            'properties': [],
            'order': 0,
            'is_binary': True,
        }
        relay_air_heater_id = ActuatorType.objects.get_by_natural_key(
            'Relay-Controlled Air Heater'
        ).pk
        res = self.client.put(
            self.url_for_object('actuatorType', relay_air_heater_id), data=data
        )
        self.assertEqual(res.status_code, 403)

    @run_with_any_layout
    def test_edit_custom_type(self):
        humidifier_id = ResourceEffect.objects.get_by_natural_key('A', 'HU').pk
        data = {
            'name': 'Magic Humidifier',
            'resource_effect' : self.url_for_object('resourceEffect', humidifier_id),
            'properties': [],
            'order': 0,
            'is_binary': True,
        }
        res = self.client.post(self.url_for_object('actuatorType'), data=data)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['name'], 'Magic Humidifier')
        data['name'] = 'New Name'
        res = self.client.put(res.data['url'], data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['name'], 'New Name')

    @run_with_any_layout
    def test_invalid_properties(self):
        heater_id = ResourceEffect.objects.get_by_natural_key('A', 'HE').pk
        water_ec_id = ResourceProperty.objects.get_by_natural_key('W', 'EC').pk
        data = {
            'name': 'test',
            'resource_effect': self.url_for_object('resourceEffect', heater_id),
            'properties': [
                self.url_for_object('resourceProperty', water_ec_id)
            ],
            'order': 0,
            'is_binary': True,
        }
        res = self.client.post(self.url_for_object('actuatorType'), data=data)
        self.assertEqual(res.status_code, 400)


class ActuatorTestCase(APITestCase):
    @run_with_any_layout
    def test_visible_fields(self):
        fields = ActuatorSerializer().get_fields()
        fields.pop('url')
        fields.pop('index')
        fields.pop('name')
        fields.pop('actuator_type')
        fields.pop('control_profile')
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
        heater_id = ActuatorType.objects.get_by_natural_key(
            'Relay-Controlled Air Heater'
        ).pk
        control_profile_id = ControlProfile.objects.get_by_natural_key(
            'Relay-Controlled Air Heater', 'Default Profile'
        ).pk
        actuator_info = {
            'actuator_type': self.url_for_object('actuatorType', heater_id),
            'control_profile': self.url_for_object(
                'controlProfile', control_profile_id
            ),
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
        circulation_id = ActuatorType.objects.get_by_natural_key(
            'Relay-Controlled Humidifier'
        ).pk
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
