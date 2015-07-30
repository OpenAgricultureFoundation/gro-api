import time
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.exceptions import APIException
from cityfarm_api.viewsets import ModelViewSet
from cityfarm_api.serializers import model_serializers
from .models import SensingPoint, DataPoint

DataPointSerializer = model_serializers.get_for_model(DataPoint)

class SensingPointViewSet(ModelViewSet):
    model = SensingPoint

    @detail_route(methods=["get"])
    def data(self, request, pk=None):
        raise NotImplementedError()

    @detail_route(methods=["get"])
    def value(self, request, pk=None):
        point = self.get_object()
        queryset = DataPoint.objects.filter(origin=point).latest()
        serializer = DataPointSerializer(
            queryset, context={'request': request}
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
        return Response(DataPoint.objects.filter(
            origin=point, timestamp__gt=since, timestamp__lt=before
        ))
