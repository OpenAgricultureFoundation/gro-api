from rest_framework import mixins
from cityfarm_api.viewsets import ModelViewSet, ReadOnlyModelViewSet
from .models import (
    PlantModel, PlantType, SowEvent, TransferEvent, HarvestEvent
)


class SowEventViewSet(ReadOnlyModelViewSet):
    model = SowEvent


class TransferEventViewSet(ReadOnlyModelViewSet):
    model = TransferEvent


class HarvestEventViewSet(ReadOnlyModelViewSet):
    model = HarvestEvent
