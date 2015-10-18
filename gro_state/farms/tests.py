from django.core.management import call_command
from django.test import TestCase, override_settings
from rest_framework.test import APITestCase
from .models import Farm, LayoutChangeAttempted, SlugChangeAttempted

class FarmSlugGenerationTestCase(TestCase):
    def test(self):
        farm = Farm.get_solo()
        farm.name = 'Test Farm'
        farm.slug = None
        farm.layout = 'tray'
        farm.save()
        self.assertEqual(farm.slug, 'test-farm')

class FarmLayoutLockingTestCase(TestCase):
    def test(self):
        call_command('configure_farm', '-l tray')
        farm = Farm.get_solo()
        farm.layout = 'bay'
        self.assertRaises(LayoutChangeAttempted, farm.save)

class FarmSlugLockingTestCaseWithParent(TestCase):
    @override_settings(PARENT_SERVER='openag.mit.edu')
    def test(self):
        call_command('configure_farm', '-s farm', '-l tray')
        farm = Farm.get_solo()
        farm.slug = 'test-farm2'
        self.assertRaises(SlugChangeAttempted, farm.save)

class FarmSlugLockingTestCaseWithoutParent(TestCase):
    def test_without_parent_server(self):
        call_command('configure_farm', '-l tray')
        farm = Farm.get_solo()
        farm.slug = 'new-slug'
        farm.save()

class FarmIsConfiguredCheckTest(APITestCase):
    def test(self):
        res = self.client.get('/farm/')
        self.assertEqual(res.status_code, 403)
        call_command('configure_farm', '-l tray')
        res = self.client.get('/farm/')
        self.assertEqual(res.status_code, 200)
