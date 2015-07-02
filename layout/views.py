from cityfarm_api.viewsets import SingletonViewSet, ModelViewSet
from layout.models import (
    Model3D, TrayLayout, PlantSiteLayout, LayoutObject, Enclosure, Tray,
    dynamic_models
)
from layout.serializers import (
    Model3DSerializer, TrayLayoutSerializer, PlantSiteLayoutSerializer,
    LayoutObjectSerializer, EnclosureSerializer, TraySerializer,
    dynamic_serializers
)

class Model3DViewSet(ModelViewSet):
    queryset = Model3D.objects.all()
    serializer_class = Model3DSerializer

class TrayLayoutViewSet(ModelViewSet):
    queryset = TrayLayout.objects.all()
    serializer_class = TrayLayoutSerializer

class PlantSiteLayoutViewSet(ModelViewSet):
    queryset = PlantSiteLayout.objects.all()
    serializer_class = PlantSiteLayoutSerializer

class LayoutObjectViewSet(ModelViewSet):
    queryset = LayoutObject.objects.all()
    serializer_class = LayoutObjectSerializer

class EnclosureViewSet(SingletonViewSet):
    model = Enclosure
    queryset = Enclosure.objects.all()
    serializer_class = EnclosureSerializer

class TrayViewSet(ModelViewSet):
    queryset = Tray.objects.all()
    serializer_class = TraySerializer

dynamic_viewsets = {}
for entity_slug, entity_model in dynamic_models.items():
    class ViewSet(ModelViewSet):
        queryset = entity_model.objects.all()
        serializer_class = dynamic_serializers[entity_slug]
    dynamic_viewsets[entity_slug] = ViewSet
