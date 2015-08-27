import time
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import detail_route
from rest_framework.exceptions import APIException
from ..data_manager.permissions import EnforceReadOnly
from .models import (
    ActuatorType, ControlProfile, ActuatorEffect, Actuator, ActuatorState
)
from .serializers import (
    ActuatorTypeSerializer, ControlProfileSerializer, ActuatorEffectSerializer,
    ActuatorSerializer, ActuatorStateSerializer
)


class ActuatorTypeViewSet(ModelViewSet):
    """ A type of actuator, such as a relay-controlled heater """
    queryset = ActuatorType.objects.all()
    serializer_class = ActuatorTypeSerializer
    permission_classes = [EnforceReadOnly, ]


class ControlProfileViewSet(ModelViewSet):
    """ A profile that holds the control settings for an actuator """
    queryset = ControlProfile.objects.all()
    serializer_class = ControlProfileSerializer
    permission_classes = [EnforceReadOnly, ]


class ActuatorEffectViewSet(ModelViewSet):
    """
    The through model from ControlProfile to ResourceProperty. Holds
    information about how an actuator controlled with the given profile should
    be operated in response to changes in the given resource property.
    """
    queryset = ActuatorEffect.objects.all()
    serializer_class = ActuatorEffectSerializer


class ActuatorViewSet(ModelViewSet):
    """ A physical actuator instance """
    queryset = Actuator.objects.all()
    serializer_class = ActuatorSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.update_override()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        for instance in queryset:
            instance.update_override()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=["post"])
    def override(self, request, pk=None):
        import pdb; pdb.set_trace()
        instance = self.get_object()
        value = request.data.get('value', None)
        if value is None:
            raise APIException(
                'No value received for "value" in the posted dictionary'
            )
        duration = request.data.get('duration', None)
        if not duration:
            raise APIException(
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
        timestamp = request.data.get('timestamp', time.time())
        value = request.data.get('value', None)
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


class ActuatorStateViewSet(ModelViewSet):
    """ The state of an actuator at a given time """
    queryset = ActuatorState.objects.all()
    serializer_class = ActuatorStateSerializer
