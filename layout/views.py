import time
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from cityfarm_api.viewsets import SingletonViewSet, ModelViewSet
from cityfarm_api.serializers import model_serializers
from recipes.models import SetPoint
from resources.models import ResourceProperty
from .models import Enclosure, Tray

SetPointSerializer = model_serializers.get_for_model(SetPoint)

class EnclosureViewSet(SingletonViewSet):
    model = Enclosure

class TrayViewSet(ModelViewSet):
    model = Tray
    @detail_route(methods=["get"])
    def set_points(self, request, pk=None):
        tray = self.get_object()
        set_points = {}
        for property in ResourceProperty.objects.all():
            set_point = SetPoint.objects.filter(
                tray=tray, property=property, timestamp__lt=time.time()
            ).latest()
            set_points[set_point.property.code] = set_point.value
        return Response(set_points)
