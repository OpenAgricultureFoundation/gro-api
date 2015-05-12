from imp import reload
from django.apps import apps
from rest_framework.test import APITestCase


class UnconfiguredFarmTestCase(APITestCase):
    fixtures = ['unconfigured_farm.json']

    def setUp(self):
        layout_app = apps.get_app.config('layout')
        print(apps.get_app_config('layout'))

    def test_models(self):
        from layout.models import all_models
        assert len(all_models) == 0

    def test_index(self):
        response = self.client.get('/')
        assert response.status_code == 200


#class GrobotFarmTestCase(APITestCase):
#    fixtures = ['grobot_farm.json']
#
#    def setUp(self):
#        reload_models()
#
#    def test_models(self):
#        from layout.models import all_models
#        assert len(all_models) != 0
#
#    def test_index(self):
#        response = self.client.get('/')
#        assert response.status_code == 200
#
#
#class MainFarmTestCase(APITestCase):
#    fixtures = ['main_farm.json']
#
#    def setUp(self):
#        reload_models()
#
#    def test_index(self):
#        response = self.client.get('/')
#        assert response.status_code == 200
