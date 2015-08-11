import time
from django.core.exceptions import ObjectDoesNotExist
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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.update_current_recipe_run()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        for instance in queryset:
            instance.update_current_recipe_run()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=["get"])
    def set_points(self, request, pk=None):
        tray = self.get_object()
        set_points = {}
        for property in ResourceProperty.objects.all():
            try:
                set_point = SetPoint.objects.filter(
                    tray=tray, property=property, timestamp__lt=time.time()
                ).latest()
            except ObjectDoesNotExist:
                continue
            else:
                code = ''.join(set_point.property.natural_key())
                set_points[code] = set_point.value
        return Response(set_points)
