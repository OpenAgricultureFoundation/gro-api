from rest_framework.response import Response
from rest_framework.decorators import detail_route
from cityfarm_api.viewsets import ModelViewSet
from cityfarm_api.permissions import EnforceReadOnly
from sensors.models import SensingPoint
from .models import ResourceType, ResourceProperty
from .serializers import ResourceTypeSerializer, ResourcePropertySerializer

class ResourceTypeViewSet(ModelViewSet):
    model = ResourceType
    permission_classes = [EnforceReadOnly,]


class ResourcePropertyViewSet(ModelViewSet):
    model = ResourceProperty
    permission_classes = [EnforceReadOnly,]
