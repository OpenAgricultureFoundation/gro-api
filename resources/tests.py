from cityfarm_api.test import APITestCase, run_with_any_layout

class ResourceTypeTestCase(APITestCase):
    @run_with_any_layout
    def test_edit_stock_type(self):
        data = {'name': 'test'}
        res = self.client.put(
            self.url_for_object('resourceType', 1), data=data
        )
        self.assertEqual(res.status_code, 403)

    @run_with_any_layout
    def test_edit_custom_type(self):
        data = {'name': 'test'}
        res = self.client.post(self.url_for_object('resourceType'), data=data)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data['name'], 'test')
        data['name'] = 'test2'
        res = self.client.put(res.data['url'], data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['name'], 'test2')

class ResourcePropertyTestCase(APITestCase):
    @run_with_any_layout
    def test_edit_stock_property(self):
        data = {
            'code': 'TS',
            'name': 'test',
            'resource_type': self.url_for_object('resourceType', 1)
        }
        res = self.client.put(
            self.url_for_object('resourceProperty', 1), data=data
        )
        self.assertEqual(res.status_code, 403)

    @run_with_any_layout
    def test_edit_custom_property(self):
        data = {
            'code': 'TS',
            'name': 'test',
            'resource_type': self.url_for_object('resourceType', 1)
        }
        res = self.client.post(
            self.url_for_object('resourceProperty'), data=data
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data['name'], 'test')
        data['name'] = 'test2'
        res = self.client.put(res.data['url'], data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['name'], 'test2')

class ResourceTestCase(APITestCase):
    @run_with_any_layout
    def test_edit_resource(self):
        data = {
            'resource_type': self.url_for_object('resourceType', 1),
            'location': self.url_for_object('enclosure', 1),
        }
        res = self.client.post(self.url_for_object('resource'), data=data)
        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.data['name'].endswith('Air Resource 1'))
        data['name'] = 'test'
        res = self.client.put(res.data['url'], data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['name'], 'test')

