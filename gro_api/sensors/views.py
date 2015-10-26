import time
import json
import django_filters
from django.core.cache import caches
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import detail_route
from rest_framework.exceptions import APIException
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from ..gro_api.filters import HistoryFilterMixin
from ..gro_api.permissions import EnforceReadOnly
from .models import SensorType, Sensor, SensingPoint, DataPoint
from .serializers import (
    SensorTypeSerializer, SensorSerializer, SensingPointSerializer,
    DataPointSerializer
)


class SensorTypeViewSet(ModelViewSet):
    """ A type of sensor, such as "DHT22" """
    queryset = SensorType.objects.all()
    serializer_class = SensorTypeSerializer
    permission_classes = [EnforceReadOnly, DjangoModelPermissionsOrAnonReadOnly]


class SensorViewSet(ModelViewSet):
    """ A physical sensor instance """
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer


class SensingPointViewSet(ModelViewSet):
    """
    Used to separate multi-output sensors into abstract single-output units.
    For example, a sensor measuring both temperature and humidity would
    generate 2 sensing points, one for temperature and one for humidity
    """
    queryset = SensingPoint.objects.all()
    serializer_class = SensingPointSerializer

    @detail_route(methods=["get"])
    def value(self, request, pk=None):
        """
        Get the current value of the sensing point
        ---
        serializer: gro_api.sensors.serializers.DataPointSerializer
        """
        instance = self.get_object()
        cache_key = 'sp_{}_value'.format(instance.pk)
        cache = caches['default']
        data = cache.get(cache_key)
        return Response(json.loads(data))


class DataPointFilter(HistoryFilterMixin):
    class Meta:
        model = DataPoint
        fields = ['sensing_point', 'min_time', 'max_time']


class DataPointViewSet(ModelViewSet):
    """ A data point recorded from a sensing point """
    queryset = DataPoint.objects.all()
    serializer_class = DataPointSerializer
    filter_class = DataPointFilter

    def create(self, request, *args, **kwargs):
        many = request.query_params.get('many', False)
        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        cache = caches['default']
        for point in serializer.data:
            sp_pk = point['sensing_point'].split('/')[-2]
            cache_key = 'sp_{}_value'.format(sp_pk)
            cache.set(cache_key, json.dumps(point), timeout=None)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        if getattr(serializer, 'many', False):
            DataPoint.objects.bulk_create([
                DataPoint(**child_attrs) for child_attrs in
                serializer.validated_data
            ])
        else:
            serializer.save()
