from rest_framework import mixins
from cityfarm_api.viewsets import ModelViewSet, ReadOnlyModelViewSet
from cityfarm_api.permissions import EnforceReadOnly
from .models import (
    PlantModel, PlantType, SowEvent, TransferEvent, HarvestEvent
)


class PlantModelViewSet(ModelViewSet):
    model = PlantModel
    permission_classes = [EnforceReadOnly,]


class PlantTypeViewSet(ModelViewSet):
    model = PlantType
    permission_classes = [EnforceReadOnly,]


class SowEventViewSet(ReadOnlyModelViewSet):
    model = SowEvent


class TransferEventViewSet(ReadOnlyModelViewSet):
    model = TransferEvent


class HarvestEventViewSet(ReadOnlyModelViewSet):
    model = HarvestEvent
