from rest_framework.viewsets import ModelViewSet
from .models import ResourceType, ResourceProperty, Resource
from .serializers import (
    ResourceTypeSerializer, ResourcePropertySerializer, ResourceSerializer
)


class ResourceTypeViewSet(ModelViewSet):
    queryset = ResourceType.objects.all()
    serializer_class = ResourceTypeSerializer


class ResourcePropertyViewSet(ModelViewSet):
    queryset = ResourceProperty.objects.all()
    serializer_class = ResourcePropertySerializer


class ResourceViewSet(ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
