from rest_framework import mixins
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from .models import (
    PlantModel, PlantType, Plant, SowEvent, TransferEvent, HarvestEvent,
    PlantComment
)
from .serializers import (
    PlantModelSerializer, PlantTypeSerializer, PlantSerializer,
    SowEventSerializer, TransferEventSerializer, HarvestEventSerializer,
    PlantCommentSerializer
)


class PlantModelViewSet(ModelViewSet):
    queryset = PlantModel.objects.all()
    serializer_class = PlantModelSerializer


class PlantTypeViewSet(ModelViewSet):
    queryset = PlantType.objects.all()
    serializer_class = PlantTypeSerializer


class PlantViewSet(ModelViewSet):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer


class SowEventViewSet(ReadOnlyModelViewSet):
    queryset = SowEvent.objects.all()
    serializer_class = SowEventSerializer


class TransferEventViewSet(ReadOnlyModelViewSet):
    queryset = TransferEvent.objects.all()
    serializer_class = TransferEventSerializer


class HarvestEventViewSet(ReadOnlyModelViewSet):
    queryset = HarvestEvent.objects.all()
    serializer_class = HarvestEventSerializer


class PlantCommentViewSet(ModelViewSet):
    queryset = PlantComment.objects.all()
    serializer_class = PlantCommentSerializer
