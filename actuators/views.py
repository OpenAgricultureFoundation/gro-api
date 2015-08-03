import time
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.exceptions import APIException
from cityfarm_api.viewsets import ModelViewSet
from cityfarm_api.serializers import model_serializers
from cityfarm_api.permissions import EnforceReadOnly
from .models import ActuatorType, Actuator, ActuatorState

ActuatorStateSerializer = model_serializers.get_for_model(ActuatorState)

class ActuatorTypeViewSet(ModelViewSet):
    model = ActuatorType
    permission_classes = [EnforceReadOnly,]

class ActuatorViewSet(ModelViewSet):
    model = Actuator

    @detail_route(methods=["get"])
    def state(self, request, pk=None):
        actuator = self.get_object()
        queryset = ActuatorState.filter(origin=actuator).latest()
        serializer = ActuatorStateSerializer(
            queryset, context={'request': request}
        )
        return Response(serializer.data)

    @detail_route(methods=["get"])
    def history(self, request, pk=None):
        actuator = self.get_object()
        since = request.query_params.get('since', None)
        if not since:
            raise APIException(
                "History requests must contain a 'since' GET parameter"
            )
        before = request.query_params.get('before', time.time())
        queryset = ActuatorState.filter(
            origin=actuator, timestamp__gt=since, timestamp__lt=before
        )
        serializer = ActuatorStateSerializer(
            queryset, context={'request': request}
        )
        return Response(serializer.data)
