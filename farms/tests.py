from django.test import TestCase
from farms.models import Farm


class FarmTestCase(TestCase):
    def test_farm_id_null(self):
        Farm.get_solo().delete()
        farm = Farm.get_solo()
        assert not farm.is_configured()

    def test_farm_id_nonzero(self):
        Farm.get_solo().delete()
        farm = Farm.get_solo()
        farm.farm_id = 69
        assert farm.is_configured()
