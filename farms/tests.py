from django.test import TestCase
from django.core.exceptions import ValidationError
from farms.models import Farm


class FarmTestCase(TestCase):
    def test_invalid_layout(self):
        farm = Farm.get_solo()
        farm.layout = 'test'
        self.assertRaises(ValidationError, farm.full_clean)

    def test_valid_layout(self):
        farm = Farm.get_solo()
        farm.layout = 'aisle'
        farm.save()

    def test_empty_slug(self):
        farm = Farm.get_solo()
        farm.slug = ''
        farm.name = 'Test Farm'
        farm.save()
        self.assertEqual(farm.name, 'Test Farm')
        self.assertEqual(farm.slug, 'test-farm')

    def test_non_empty_slug(self):
        farm = Farm.get_solo()
        farm.slug = 'test'
        farm.name = 'Test Farm'
        self.assertEqual(farm.name, 'Test Farm')
        self.assertEqual(farm.slug, 'test')
