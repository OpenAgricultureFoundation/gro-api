import time
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import detail_route
from rest_framework.exceptions import APIException
from ..data_manager.permissions import EnforceReadOnly
from .models import SensorType, Sensor, SensingPoint, DataPoint
from .serializers import (
    SensorTypeSerializer, SensorSerializer, SensingPointSerializer,
    DataPointSerializer
)


class SensorTypeViewSet(ModelViewSet):
    queryset = SensorType.objects.all()
    serializer_class = SensorTypeSerializer
    permission_classes = [EnforceReadOnly, ]


class SensorViewSet(ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer


class SensingPointViewSet(ModelViewSet):
    queryset = SensingPoint.objects.all()
    serializer_class = SensingPointSerializer

    @detail_route(methods=["get"])
    def data(self, request, pk=None):
        raise NotImplementedError()

    @detail_route(methods=["get", "post"])
    def value(self, request, pk=None):
        if request.method == "GET":
            return self.get_value(request, pk=pk)
        elif request.method == "POST":
            return self.post_value(request, pk=pk)
        else:
            raise ValueError()

    def get_value(self, request, pk=None):
        instance = self.get_object()
        try:
            queryset = DataPoint.objects.filter(origin=instance).latest()
        except ObjectDoesNotExist:
            raise APIException(
                'No data has been recorded for this sensor yet'
            )
        serializer = DataPointSerializer(
            queryset, context={'request': request}
        )
        return Response(serializer.data)

    def post_value(self, request, pk=None):
        instance = self.get_object()
        timestamp = request.DATA.get('timestamp', time.time())
        value = request.DATA.get('value')
        if value is None:
            raise APIException(
                'No value received for "value" in the posted dictionary'
            )
        data_point = DataPoint(
            origin=instance, timestamp=timestamp, value=value
        )
        data_point.save()
        serializer = DataPointSerializer(
            data_point, context={'request': request}
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
        queryset = DataPoint.objects.filter(
            origin=instance, timestamp__gt=since, timestamp__lt=before
        )
        serializer = DataPointSerializer(
            queryset, context={'request': request}
        )
        return Response(serializer.data)


class DataPointViewSet(ModelViewSet):
    queryset = DataPoint.objects.all()
    serializer_class = DataPoint.objects.all()

    def create(self, request, *args, **kwargs):
        many = request.QUERY_PARAMS.get('many', False)
        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        if getattr(serializer, 'many', False):
            self.model.objects.bulk_create([
                self.model(**child_attrs) for child_attrs in
                serializer.validated_data
            ])
        else:
            serializer.save()
