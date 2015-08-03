from rest_framework.response import Response
from rest_framework.decorators import detail_route
from cityfarm_api.viewsets import ModelViewSet
from cityfarm_api.permissions import EnforceReadOnly
from sensors.models import SensingPoint
from .models import ResourceType, ResourceProperty
from .serializers import ResourcePropertySerializer

class ResourceTypeViewSet(ModelViewSet):
    model = ResourceType
    permission_classes = [EnforceReadOnly,]

class ResourcePropertyViewSet(ModelViewSet):
    model = ResourceProperty
    permission_classes = [EnforceReadOnly,]

    @detail_route(methods=["get"])
    def sensing_points_by_sensor(self, request, pk=None):
        serializer = ResourcePropertySerializer(
            self.get_object(), context={'request': request}
        )
        return Response(serializer.sensing_points_by_sensor())
