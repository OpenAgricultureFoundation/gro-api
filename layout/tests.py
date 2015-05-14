from django.conf import settings
from solo.models import SingletonModel
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
        def test_models(self):
            from layout.models import all_models
            assert len(all_models) == 0
        def test_serializers(self):
            from layout.serializers import all_serializers
            assert len(all_serializers) == 0
        def test_viewsets(self):
            from layout.views import all_viewsets
            assert len(all_viewsets) == 0
elif test_config == LAYOUT_TEST_TRAY:
    class TrayFarmTestCase(APITestCase):
        def test_models(self):
            from layout.models import all_models, Object3D, LocationMixin
            assert len(all_models) == 1
            assert "tray" in all_models
            tray_models = all_models["tray"].copy()
            # Check LayoutObject
            assert "layout_object" in tray_models
            assert tray_models["layout_object"].__name__ == "tray_layout_object"
            LayoutObject = tray_models.pop("layout_object")
            # Check Enclosure
            assert "enclosure" in tray_models
            assert tray_models["enclosure"].__name__ == "tray_enclosure"
            Enclosure = tray_models.pop("enclosure")
            assert issubclass(Enclosure, LayoutObject)
            assert issubclass(Enclosure, Object3D)
            assert issubclass(Enclosure, SingletonModel)
            # Check Tray
            assert "tray" in tray_models
            assert tray_models["tray"].__name__ == "tray_tray"
            Tray = tray_models.pop("tray")
            assert issubclass(Tray, LayoutObject)
            assert issubclass(Tray, Object3D)
            assert issubclass(Tray, SingletonModel)
            assert issubclass(Tray, LocationMixin)
            # Make sure there is nothing left
            assert len(tray_models) == 0
        def test_serializers(self):
            from layout.serializers import all_serializers
            assert len(all_serializers) == 1
            assert "tray" in all_serializers
            tray_serializers = all_serializers["tray"].copy()
            # Make sure all the proper serializers have been created
            assert "layout_object" in tray_serializers
            tray_serializers.pop("layout_object")
            assert "enclosure" in tray_serializers
            tray_serializers.pop("enclosure")
            assert "tray" in tray_serializers
            tray_serializers.pop("tray")
            # Make sure there is nothing left
            assert len(tray_serializers) == 0
        def test_viewsets(self):
            from layout.views import all_viewsets
            assert len(all_viewsets) == 1
            assert "tray" in all_viewsets
            tray_viewsets = all_viewsets["tray"]
            # Make sure all the proper viewsets have been created
            assert "layout_object" in tray_viewsets
            tray_viewsets.pop("layout_object")
            assert "enclosure" in tray_viewsets
            tray_viewsets.pop("enclosure")
            assert "tray" in tray_viewsets
            tray_viewsets.pop("tray")
            # Make sure there is nothing left
            assert len(tray_viewsets) == 0
elif test_config == LAYOUT_TEST_BAY:
    class BayFarmTestCase(APITestCase):
        def test_models(self):
            from layout.models import all_models, Object3D, LocationMixin
            assert len(all_models) == 1
            assert "bay" in all_models
            bay_models = all_models["bay"].copy()
            # Check LayoutObject
            assert "layout_object" in bay_models
            assert bay_models["layout_object"].__name__ == "bay_layout_object"
            LayoutObject = bay_models.pop("layout_object")
            # Check Enclosure
            assert "enclosure" in bay_models
            assert bay_models["enclosure"].__name__ == "bay_enclosure"
            Enclosure = bay_models.pop("enclosure")
            assert issubclass(Enclosure, LayoutObject)
            assert issubclass(Enclosure, Object3D)
            assert issubclass(Enclosure, SingletonModel)
            # Check Bay
            assert "bay" in bay_models
            assert bay_models["bay"].__name__ == "bay_bay"
            Bay = bay_models.pop("bay")
            assert issubclass(Bay, LayoutObject)
            assert issubclass(Bay, Object3D)
            assert issubclass(Bay, SingletonModel)
            assert issubclass(Bay, LocationMixin)
            # Check Tray
            assert "tray" in bay_models
            assert bay_models["tray"].__name__ == "bay_tray"
            Tray = bay_models.pop("tray")
            assert issubclass(Tray, LayoutObject)
            assert issubclass(Tray, Object3D)
            assert not issubclass(Tray, SingletonModel)
            assert issubclass(Tray, LocationMixin)
            # Make sure there is nothing left
            assert len(bay_models) == 0
        def test_serializers(self):
            from layout.serializers import all_serializers
            assert len(all_serializers) == 1
            assert "bay" in all_serializers
            bay_serializers = all_serializers["bay"].copy()
            # Make sure the proper serializers have been created
            assert "layout_object" in bay_serializers
            bay_serializers.pop("layout_object")
            assert "enclosure" in bay_serializers
            bay_serializers.pop("enclosure")
            assert "bay" in bay_serializers
            bay_serializers.pop("bay")
            assert "tray" in bay_serializers
            bay_serializers.pop("tray")
            # Make sure there is nothing left
            assert len(bay_serializers) == 0
        def test_viewsets(self):
            from layout.views import all_viewsets
            assert len(all_viewsets) == 1
            assert "bay" in all_viewsets
            bay_viewsets = all_viewsets["bay"].copy()
            # Make sure all the proper viewsets have been created
            assert "layout_object" in bay_viewsets
            bay_viewsets.pop("layout_object")
            assert "enclosure" in bay_viewsets
            bay_viewsets.pop("enclosure")
            assert "bay" in bay_viewsets
            bay_viewsets.pop("bay")
            assert "tray" in bay_viewsets
            bay_viewsets.pop("tray")
            # Make sure there is nothing left
            assert len(bay_viewsets) == 0
elif test_config == LAYOUT_TEST_AISLE:
    class AisleFarmTestCase(APITestCase):
        def test_models(self):
            from layout.models import all_models, Object3D, LocationMixin
            assert len(all_models) == 1
            assert "aisle" in all_models
            aisle_models = all_models["aisle"].copy()
            # Check LayoutObject
            assert "layout_object" in aisle_models
            assert aisle_models["layout_object"].__name__ == "aisle_layout_object"
            LayoutObject = aisle_models.pop("layout_object")
            # Check Enclosure
            assert "enclosure" in aisle_models
            assert aisle_models["enclosure"].__name__ == "aisle_enclosure"
            Enclosure = aisle_models.pop("enclosure")
            assert issubclass(Enclosure, LayoutObject)
            assert issubclass(Enclosure, Object3D)
            assert issubclass(Enclosure, SingletonModel)
            # Check Aisle
            assert "aisle" in aisle_models
            assert aisle_models["aisle"].__name__ == "aisle_aisle"
            Aisle = aisle_models.pop("aisle")
            assert issubclass(Aisle, LayoutObject)
            assert issubclass(Aisle, Object3D)
            assert issubclass(Aisle, SingletonModel)
            assert issubclass(Aisle, LocationMixin)
            # Check Bay
            assert "bay" in aisle_models
            assert aisle_models["bay"].__name__ == "aisle_bay"
            Bay = aisle_models.pop("bay")
            assert issubclass(Bay, LayoutObject)
            assert issubclass(Bay, Object3D)
            assert not issubclass(Bay, SingletonModel)
            assert issubclass(Bay, LocationMixin)
            # Check Tray
            assert "tray" in aisle_models
            assert aisle_models["tray"].__name__ == "aisle_tray"
            Tray = aisle_models.pop("tray")
            assert issubclass(Tray, LayoutObject)
            assert issubclass(Tray, Object3D)
            assert not issubclass(Tray, SingletonModel)
            assert issubclass(Tray, LocationMixin)
            assert len(aisle_models) == 0
        def test_serializers(self):
            from layout.serializers import all_serializers
            assert len(all_serializers) == 1
            # Make sure the proper serializers have been created
            assert "aisle" in all_serializers
            aisle_serializers = all_serializers["aisle"].copy()
            assert "layout_object" in aisle_serializers
            aisle_serializers.pop("layout_object")
            assert "enclosure" in aisle_serializers
            aisle_serializers.pop("enclosure")
            assert "aisle" in aisle_serializers
            aisle_serializers.pop("aisle")
            assert "bay" in aisle_serializers
            aisle_serializers.pop("bay")
            assert "tray" in aisle_serializers
            aisle_serializers.pop("tray")
            # Make sure there is nothing left
            assert len(aisle_serializers) == 0
        def test_viewsets(self):
            from layout.views import all_viewsets
            assert len(all_viewsets) == 1
            # Make sure the proper viewsets have been created
            assert "aisle" in all_viewsets
            aisle_viewsets = all_viewsets["aisle"].copy()
            assert "layout_object" in aisle_viewsets
            aisle_viewsets.pop("layout_object")
            assert "enclosure" in aisle_viewsets
            aisle_viewsets.pop("enclosure")
            assert "aisle" in aisle_viewsets
            aisle_viewsets.pop("aisle")
            assert "bay" in aisle_viewsets
            aisle_viewsets.pop("bay")
            assert "tray" in aisle_viewsets
            aisle_viewsets.pop("tray")
            # Make sure there is nothing left
            assert len(aisle_viewsets) == 0
