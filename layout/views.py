from solo.models import SingletonModel
from django.shortcuts import render
from rest_framework import viewsets, generics, mixins
from layout.models import (Model3D, TrayLayout, PlantSiteLayout, LayoutObject,
        Enclosure, Tray, dynamic_models)
from layout.serializers import  (Model3DSerializer, TrayLayoutSerializer,
        PlantSiteLayoutSerializer, LayoutObjectSerializer, EnclosureSerializer,
        TraySerializer, dynamic_serializers)
from cityfarm_api.viewsets import SingletonViewSet

class Model3DViewset(viewsets.ModelViewSet):
    queryset = Model3D.objects.all()
    serializer_class = Model3DSerializer

class TrayLayoutViewset(viewsets.ModelViewSet):
    queryset = TrayLayout.objects.all()
    serializer_class = TrayLayoutSerializer

class PlantSiteLayoutViewset(viewsets.ModelViewSet):
    queryset = PlantSiteLayout.objects.all()
    serializer_class = PlantSiteLayoutSerializer

class LayoutObjectViewset(viewsets.ModelViewSet):
    queryset = LayoutObject.objects.all()
    serializer_class = LayoutObjectSerializer

class EnclosureViewset(viewsets.ModelViewSet):
    queryset = Enclosure.objects.all()
    serializer_class = EnclosureSerializer

class TrayViewset(viewsets.ModelViewSet):
    queryset = Tray.objects.all()
    serializer_class = TraySerializer

dynamic_viewsets = {}
for entity_name, entity_model in dynamic_models.items():
    class Viewset(viewsets.ModelViewSet):
        queryset = entity_model.objects.all()
        serializer_class = dynamic_serializers[entity_name]
    dynamic_viewsets[entity_name] = Viewset
