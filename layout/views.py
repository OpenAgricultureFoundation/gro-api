from solo.models import SingletonModel
from django.shortcuts import render
from rest_framework import viewsets, generics, mixins
from layout.models import (Model3D, TrayLayout, PlantSiteLayout, LayoutObject,
        Enclosure, Tray, dynamic_models)
from layout.serializers import  (Model3DSerializer, TrayLayoutSerializer,
        PlantSiteLayoutSerializer, LayoutObjectSerializer, EnclosureSerializer,
        TraySerializer, dynamic_serializers)
from cityfarm_api.viewsets import SingletonViewSet

class Model3DViewSet(viewsets.ModelViewSet):
    queryset = Model3D.objects.all()
    serializer_class = Model3DSerializer

class TrayLayoutViewSet(viewsets.ModelViewSet):
    queryset = TrayLayout.objects.all()
    serializer_class = TrayLayoutSerializer

class PlantSiteLayoutViewSet(viewsets.ModelViewSet):
    queryset = PlantSiteLayout.objects.all()
    serializer_class = PlantSiteLayoutSerializer

class LayoutObjectViewSet(viewsets.ModelViewSet):
    queryset = LayoutObject.objects.all()
    serializer_class = LayoutObjectSerializer

class EnclosureViewSet(SingletonViewSet):
    model = Enclosure
    queryset = Enclosure.objects.all()
    serializer_class = EnclosureSerializer

class TrayViewSet(viewsets.ModelViewSet):
    queryset = Tray.objects.all()
    serializer_class = TraySerializer

dynamic_viewsets = {}
for entity_slug, entity_model in dynamic_models.items():
    class ViewSet(viewsets.ModelViewSet):
        queryset = entity_model.objects.all()
        serializer_class = dynamic_serializers[entity_slug]
    dynamic_viewsets[entity_slug] = ViewSet
