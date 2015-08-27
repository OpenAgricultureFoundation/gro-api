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
    """ A 3D model of a plant """
    queryset = PlantModel.objects.all()
    serializer_class = PlantModelSerializer


class PlantTypeViewSet(ModelViewSet):
    """ A type of plant. These are organized as a tree. """
    queryset = PlantType.objects.all()
    serializer_class = PlantTypeSerializer


class PlantViewSet(ModelViewSet):
    """ A plant that was grown or is being grown in the system."""
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer


class SowEventViewSet(ReadOnlyModelViewSet):
    """ A log of when each plant was sown """
    queryset = SowEvent.objects.all()
    serializer_class = SowEventSerializer


class TransferEventViewSet(ReadOnlyModelViewSet):
    """
    A log of every time a plant was transfered from one plant site to another
    """
    queryset = TransferEvent.objects.all()
    serializer_class = TransferEventSerializer


class HarvestEventViewSet(ReadOnlyModelViewSet):
    """ A log of when each plant was harvested """
    queryset = HarvestEvent.objects.all()
    serializer_class = HarvestEventSerializer


class PlantCommentViewSet(ModelViewSet):
    """ A user-provided comment on a plant """
    queryset = PlantComment.objects.all()
    serializer_class = PlantCommentSerializer
