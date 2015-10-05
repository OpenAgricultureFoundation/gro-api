from ..gro_api.test import APITestCase, run_with_layouts
from .models import Farm, LayoutChangeAttempted, SlugChangeAttempted

class FarmSlugGenerationTestCase(APITestCase):
    @run_with_layouts(None)
    def test(self):
        farm = Farm.get_solo()
        farm.name = 'Test Farm'
        farm.slug = None
        farm.layout = 'tray'
        farm.save()
        self.assertEqual(farm.slug('test-farm'))

class FarmLayoutLockingTestCase(APITestCase):
    @run_with_layouts(None)
    def test(self):
        farm = Farm.get_solo()
        farm.name = 'Test Farm'
        farm.layout = 'tray'
        farm.save()
        farm.layout = 'bay'
        self.assertRaises(LayoutChangeAttempted, farm.save)

class FarmSlugLockingTestCase(APITestCase):
    @run_with_layouts(None)
    def test(self):
        farm = Farm.get_solo()
        farm.name = 'Test Farm'
        farm.layout = 'tray'
        farm.save()
        farm.slug = 'test-farm2'
        self.assertRaises(SlugChangeAttempted, farm.save)
