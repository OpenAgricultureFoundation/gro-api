import time
import django_filters
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import detail_route
from rest_framework.exceptions import APIException
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from ..gro_api.permissions import EnforceReadOnly
from ..gro_api.filters import HistoryFilterMixin
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
    permission_classes = [EnforceReadOnly, DjangoModelPermissionsOrAnonReadOnly]


class ControlProfileViewSet(ModelViewSet):
    """ A profile that holds the control settings for an actuator """
    queryset = ControlProfile.objects.all()
    serializer_class = ControlProfileSerializer
    permission_classes = [EnforceReadOnly, DjangoModelPermissionsOrAnonReadOnly]


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

    # TODO: Remove this once frontend switches to new override endpoint
    @detail_route(methods=["post"])
    def override(self, request, pk=None):
        """
        DEPRECATED
        ---
        response_serializer: gro_api.recipes.serializers.ActuatorOverrideSerializer
        """
        from ..recipes.serializers import ActuatorOverrideSerializer
        instance = self.get_object()
        data = dict(request.data)
        data['start_timestamp'] = time.time()
        data['end_timestamp'] = data['start_timestamp'] + data['duration']
        data.pop('duration')
        data['actuator'] = instance
        serializer = ActuatorOverrideSerializer(**data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @detail_route(methods=["get"])
    def state(self, request, pk=None):
        """
        Get the current state of the actuator
        ---
        serializer: gro_api.actuators.serializers.ActuatorStateSerializer
        """
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


class ActuatorStateFilter(HistoryFilterMixin):
    class Meta:
        model = ActuatorState
        fields = ['actuator', 'min_time', 'max_time']


class ActuatorStateViewSet(ModelViewSet):
    """ The state of an actuator at a given time """
    queryset = ActuatorState.objects.all()
    serializer_class = ActuatorStateSerializer
    filter_class = ActuatorStateFilter

    def create(self, request, *args, **kwargs):
        many = request.query_params.get('many', False)
        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_value(raise_exception=True)
        self.perform_create(serializer)

    def perform_create(self, serializer):
        if getattr(serializer, 'many', False):
            ActuatorState.objects.bulk_create([
                ActuatorState(**child_attrs) for child_attrs in
                serializer.validated_data
            ])
        else:
            serializer.save()
