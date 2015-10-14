import time
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.viewsets import ModelViewSet
from ..core.viewsets import SingletonModelViewSet, BulkModelViewSet
from ..core.permissions import IsAdminOrReadOnly
from ..recipes.models import SetPoint
from ..resources.models import ResourceProperty
from .serializers import (
    LayoutModel3DSerializer, TrayLayoutSerializer, PlantSiteLayoutSerializer,
    EnclosureSerializer, TraySerializer, PlantSiteSerializer,
    dynamic_serializers
)
from .models import (
    LayoutModel3D, TrayLayout, PlantSiteLayout, Enclosure, Tray, PlantSite,
    dynamic_models
)


class LayoutModel3DViewSet(ModelViewSet):
    """ A 3D model of a farm component """
    queryset = LayoutModel3D.objects.all()
    serializer_class = LayoutModel3DSerializer
    permission_classes = [IsAdminOrReadOnly,]


class TrayLayoutViewSet(ModelViewSet):
    """ The arrangement of plant sites in a tray """
    queryset = TrayLayout.objects.all()
    serializer_class = TrayLayoutSerializer


class PlantSiteLayoutViewSet(BulkModelViewSet):
    """ A site in a TrayLayout """
    queryset = PlantSiteLayout.objects.all()
    serializer_class = PlantSiteLayoutSerializer


class EnclosureViewSet(SingletonModelViewSet):
    """ The top-level object in the layout tree """
    model = Enclosure
    queryset = Enclosure.objects.all()
    serializer_class = EnclosureSerializer


class TrayViewSet(ModelViewSet):
    """ The lowest level in the layout tree; contains plant sites """
    model = Tray
    queryset = Tray.objects.all()
    serializer_class = TraySerializer

    @detail_route(methods=["get"])
    def set_points(self, request, pk=None):
        """
        Get a dictionary mapping resource property codes to current set point
        values
        """
        tray = self.get_object()
        set_points = {}
        for property in ResourceProperty.objects.all():
            try:
                set_point = SetPoint.objects.filter(
                    tray=tray, property=property, timestamp__lt=time.time()
                ).latest()
            except ObjectDoesNotExist:
                continue
            else:
                code = ''.join(set_point.property.natural_key())
                set_points[code] = set_point.value
        return Response(set_points)


class PlantSiteViewSet(ModelViewSet):
    """ A growing site in which a plant can be planted """
    queryset = PlantSite.objects.all()
    serializer_class = PlantSiteSerializer


dynamic_viewsets = {}
for model_name in dynamic_models.keys():
    Model = dynamic_models[model_name]
    Serializer = dynamic_serializers[model_name]
    viewset_attrs = {
        'queryset': Model.objects.all(),
        'serializer_class': Serializer,
        '__doc__': Model.__doc__,
    }
    viewset_name = '{}ViewSet'.format(Model.__name__)
    ViewSet = type(viewset_name, (ModelViewSet,), viewset_attrs)
    dynamic_viewsets[model_name] = ViewSet
