from rest_framework.viewsets import ModelViewSet
from ..data_manager.permissions import EnforceReadOnly
from .models import (
    ResourceType, ResourceProperty, ResourceEffect, Resource
)
from .serializers import (
    ResourceTypeSerializer, ResourcePropertySerializer,
    ResourceEffectSerializer, ResourceSerializer
)


class ResourceTypeViewSet(ModelViewSet):
    queryset = ResourceType.objects.all()
    serializer_class = ResourceTypeSerializer
    permission_classes = [EnforceReadOnly, ]


class ResourcePropertyViewSet(ModelViewSet):
    queryset = ResourceProperty.objects.all()
    serializer_class = ResourcePropertySerializer
    permission_classes = [EnforceReadOnly, ]


class ResourceEffectViewSet(ModelViewSet):
    queryset = ResourceEffect.objects.all()
    serializer_class = ResourceEffectSerializer
    permission_classes = [EnforceReadOnly, ]


class ResourceViewSet(ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
