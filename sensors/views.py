import time
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.exceptions import APIException
from cityfarm_api.viewsets import ModelViewSet, ReadOnlyModelViewSet
from cityfarm_api.serializers import model_serializers
from cityfarm_api.permissions import EnforceReadOnly
from .models import SensorType, SensingPoint, DataPoint

DataPointSerializer = model_serializers.get_for_model(DataPoint)

class SensorTypeViewSet(ModelViewSet):
    model = SensorType
    permission_classes = [EnforceReadOnly,]


class SensingPointViewSet(ReadOnlyModelViewSet):
    model = SensingPoint

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
        point = self.get_object()
        try:
            queryset = DataPoint.objects.filter(origin=point).latest()
        except ObjectDoesNotExist:
            raise APIException(
                'No data has been recorded for this sensor yet'
            )
        serializer = DataPointSerializer(
            queryset, context={'request': request}
        )
        return Response(serializer.data)

    def post_value(self, request, pk=None):
        sensing_point = self.get_object()
        timestamp = request.DATA.get('timestamp', time.time())
        value = request.DATA.get('value')
        if value is None:
            raise APIException(
                'No value received for "value" in the posted dictionary'
            )
        data_point = DataPoint(
            origin=sensing_point, timestamp=timestamp, value=value
        )
        data_point.save()
        serializer = DataPointSerializer(
            data_point, context={'request': request}
        )
        return Response(serializer.data)

    @detail_route(methods=["get"])
    def history(self, request, pk=None):
        point = self.get_object()
        since = request.query_params.get('since', None)
        if not since:
            raise APIException(
                "History requests must contain a 'since' GET parameter"
            )
        before = request.query_params.get('before', time.time())
        queryset = DataPoint.objects.filter(
            origin=point, timestamp__gt=since, timestamp__lt=before
        )
        serializer = DataPointSerializer(
            queryset, context={'request': request}
        )
        return Response(serializer.data)
