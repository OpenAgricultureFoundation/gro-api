from cityfarm_api.viewsets import ModelViewSet
from cityfarm_api.permissions import EnforceReadOnly
from .models import ResourceType, ResourceProperty

class ResourceTypeViewSet(ModelViewSet):
    model = ResourceType
    permission_classes = [EnforceReadOnly,]

class ResourcePropertyViewSet(ModelViewSet):
    model = ResourceProperty
    permission_classes = [EnforceReadOnly,]
