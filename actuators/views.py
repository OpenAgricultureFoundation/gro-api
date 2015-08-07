import time
from django.core.exceptions import ObjectDoesNotExist
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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.override_value and \
                instance.override_timeout <= time.time():
            instance.override_value = None
            instance.override_timeout = None
            instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @detail_route(methods=["post"])
    def override(self, request, pk=None):
        instance = self.get_object()
        value = request.DATA.get('value', None)
        if value is None:
            raise APIException(
                'No value received for "value" in the posted dictionary'
            )
        duration = request.DATA.get('duration', None)
        if not duration:
            raise APIExcpetion(
                'No value received for "duration" in the posted dictionary'
            )
        instance.override_value = float(value)
        instance.override_timeout = time.time() + int(duration)
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @detail_route(methods=["get", "post"])
    def state(self, request, pk=None):
        if request.method == "GET":
            return self.get_state(request, pk=pk)
        elif request.method == "POST":
            return self.post_state(request, pk=pk)
        else:
            raise ValueError()

    def get_state(self, request, pk=None):
        instance = self.get_object()
        try:
            queryset = ActuatorState.objects.filter(origin=instance).latest()
        except ObjectDoesNotExist:
            raise APIException(
                'No state has been recorded for this actuator yet'
            )
        serializer = ActuatorStateSerializer(
            queryset, context={'request': request}
        )
        return Response(serializer.data)

    def post_state(self, request, pk=None):
        instance = self.get_object()
        timestamp = request.DATA.get('timestamp', time.time())
        value = request.DATA.get('value', None)
        if value is None:
            raise APIException(
                'No value received for "value" in the posted dictionary'
            )
        actuator_state = ActuatorState(
            origin=instance, timestamp=timestamp, value=value
        )
        actuator_state.save()
        serializer = ActuatorStateSerializer(
            actuator_state, context={'request': request}
        )
        return Response(serializer.data)

    @detail_route(methods=["get"])
    def history(self, request, pk=None):
        instance = self.get_object()
        since = request.query_params.get('since', None)
        if not since:
            raise APIException(
                "History requests must contain a 'since' GET parameter"
            )
        before = request.query_params.get('before', time.time())
        queryset = ActuatorState.filter(
            origin=instance, timestamp__gt=since, timestamp__lt=before
        )
        serializer = ActuatorStateSerializer(
            queryset, context={'request': request}
        )
        return Response(serializer.data)
