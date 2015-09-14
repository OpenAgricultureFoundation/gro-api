from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from ..gro_api.test import APITestCase, run_with_any_layout
from .models import ResourceType, ResourceProperty, Resource
from .serializers import (
    ResourceTypeSerializer, ResourcePropertySerializer,
    ResourceEffectSerializer, ResourceSerializer
)

class ResourceAuthMixin:
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            'resources', 'resources@test.com', 'resources'
        )
        layout_editors_group = Group.objects.get(name='LayoutEditors')
        cls.user.groups.add(layout_editors_group)

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        self.client.force_authenticate()

class ResourceTypeTestCase(APITestCase):
    @run_with_any_layout
    def test_visible_fields(self):
        fields = ResourceTypeSerializer().get_fields()
        fields.pop('url')
        fields.pop('code')
        fields.pop('name')
        fields.pop('resource_count')
        fields.pop('read_only')
        fields.pop('properties')
        fields.pop('effects')
        fields.pop('resources')
        fields.pop('sensor_types')
        self.assertFalse(fields)

    @run_with_any_layout
    def test_edit_stock_type(self):
        data = {'code': 'A', 'name': 'test'}
        air_id = ResourceType.objects.get_by_natural_key('A').pk
        res = self.client.put(
            self.url_for_object('resourceType', air_id), data=data
        )
        self.assertEqual(res.status_code, 403)


class ResourcePropertyTestCase(APITestCase):
    @run_with_any_layout
    def test_visible_fields(self):
        fields = ResourcePropertySerializer().get_fields()
        fields.pop('url')
        fields.pop('code')
        fields.pop('name')
        fields.pop('units')
        fields.pop('resource_type')
        fields.pop('min_operating_value')
        fields.pop('max_operating_value')
        fields.pop('read_only')
        fields.pop('sensing_point_count')
        fields.pop('sensing_points')
        fields.pop('sensor_types')
        fields.pop('actuator_types')
        self.assertFalse(fields)

    @run_with_any_layout
    def test_edit_stock_property(self):
        air_id = ResourceType.objects.get_by_natural_key('A').pk
        air_temp_id = ResourceProperty.objects.get_by_natural_key(
            'A', 'TM'
        ).pk
        data = {
            'code': 'ATS',
            'name': 'Air Test',
            'resource_type': self.url_for_object('resourceType', air_id),
            'min_operating_value': 0,
            'max_operating_value': 1,
        }
        res = self.client.put(
            self.url_for_object('resourceProperty', air_temp_id), data=data
        )
        self.assertEqual(res.status_code, 403)


class ResourceTestCase(ResourceAuthMixin, APITestCase):
    @run_with_any_layout
    def test_visible_fields(self):
        fields = ResourceSerializer().get_fields()
        fields.pop('url')
        fields.pop('index')
        fields.pop('name')
        fields.pop('resource_type')
        fields.pop('location')
        fields.pop('sensors')
        fields.pop('actuators')
        self.assertFalse(fields)

    @run_with_any_layout
    def test_resource_creation(self):
        air_id = ResourceType.objects.get_by_natural_key('A').pk
        # Create the resource
        data = {
            'resource_type': self.url_for_object('resourceType', air_id),
            'location': self.url_for_object('enclosure', 1),
        }
        res = self.client.post(self.url_for_object('resource'), data=data)
        self.assertEqual(res.status_code, 201)
        # Validate the index and name
        resource_type = self.client.get(data['resource_type']).data
        num_resources = resource_type['resource_count']
        self.assertEqual(res.data['index'], num_resources)
        expected_name = "{} Resource {}".format(
            resource_type['name'], num_resources
        )
        self.assertEqual(res.data['name'], expected_name)
        # Change the name
        data['name'] = 'test'
        res = self.client.put(res.data['url'], data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['name'], 'test')
        # Try changing the type
        water_id = ResourceType.objects.get_by_natural_key('W').pk
        data['resource_type'] = self.url_for_object('resourceType', water_id)
        res = self.client.put(res.data['url'], data=data)
        self.assertEqual(res.status_code, 400)
