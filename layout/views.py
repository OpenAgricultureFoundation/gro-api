import time
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import detail_route
from cityfarm_api.viewsets import SingletonModelViewSet
from recipes.models import SetPoint
from resources.models import ResourceProperty
from .serializers import (
    Model3DSerializer, TrayLayoutSerializer, PlantSiteLayoutSerializer,
    EnclosureSerializer, TraySerializer, PlantSiteSerializer,
    dynamic_serializers
)
from .models import (
    Model3D, TrayLayout, PlantSiteLayout, Enclosure, Tray, PlantSite,
    dynamic_models
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


class EnclosureViewSet(SingletonModelViewSet):
    model = Enclosure
    queryset = Enclosure.objects.all()
    serializer_class = EnclosureSerializer


class TrayViewSet(ModelViewSet):
    model = Tray
    queryset = Tray.objects.all()
    serializer_class = TraySerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.update_current_recipe_run()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        for instance in queryset:
            instance.update_current_recipe_run()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=["get"])
    def set_points(self, request, pk=None):
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
    queryset = PlantSite.objects.all()
    serializer_class = PlantSiteSerializer


dynamic_viewsets = {}
for model_name in dynamic_models.keys():
    Model = dynamic_models[model_name]
    Serializer = dynamic_serializers[model_name]
    class ViewSet(ModelViewSet):
        class Meta:
            model = Model
            queryset = Model.objects.all()
            serializer_class = Serializer
    dynamic_viewsets[model_name] = ViewSet
