from django.test import TestCase
from django.core.exceptions import ValidationError
from farms.models import Farm


class FarmTestCase(TestCase):
    def test_slug_generation(self):
        farm = Farm.get_solo()
        farm.slug = ''
        farm.name = 'Test Farm'
        farm.clean()
        self.assertEqual(farm.name, 'Test Farm')
        self.assertEqual(farm.slug, 'test-farm')
        farm.name = 'Different Farm'
        farm.clean()
        self.assertEqual(farm.name, 'Different Farm')
        self.assertEqual(farm.slug, 'test-farm')

    def test_layout_locking(self):
        farm = Farm.get_solo()
        farm.layout = None
        farm.clean()
        farm.layout = 'aisle'
        farm.clean()
        farm.layout = 'bay'
        self.assertRaises(ValidationError, farm.clean)
