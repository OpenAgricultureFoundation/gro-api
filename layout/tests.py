from django.conf import settings
from rest_framework.test import APITestCase
from layout.test_settings import (
    LAYOUT_TEST_UNCONFIGURED,
    LAYOUT_TEST_TRAY,
    LAYOUT_TEST_BAY,
    LAYOUT_TEST_AISLE
)


test_config = getattr(settings, "LAYOUT_TEST_CONFIGURATION", None)
if test_config == LAYOUT_TEST_UNCONFIGURED:
    class UnconfiguredFarmTestCase(APITestCase):
        fixtures = ['unconfigured_farm.json']

        def test_models(self):
            from layout.models import all_models
            assert len(all_models) == 0

        def test_index(self):
            response = self.client.get('/')
            assert response.status_code == 200
elif test_config == LAYOUT_TEST_TRAY:
    pass
elif test_config == LAYOUT_TEST_BAY:
    pass
elif test_config == LAYOUT_TEST_AISLE:
    pass
