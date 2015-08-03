from collections import OrderedDict
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import get_script_prefix, resolve, Resolver404
from django.utils.six.moves.urllib import parse as urlparse
from rest_framework.relations import HyperlinkedRelatedField
from rest_framework.serializers import HyperlinkedIdentityField
from rest_framework.utils.field_mapping import get_detail_view_name
from cityfarm_api.utils.state import system_layout
from cityfarm_api.serializers import (
    BaseSerializer, model_serializers, DUMMY_VIEW_NAME
)
from layout.models import Enclosure, Tray, dynamic_models
from layout.schemata import all_schemata
from sensors.models import SensingPoint
from .models import ResourceProperty, Resource

class ResourcePropertySerializer(BaseSerializer):
    class Meta:
        model = ResourceProperty

    def sensing_points_by_sensor(self):
        sensing_point_view_name = get_detail_view_name(SensingPoint)
        field = HyperlinkedIdentityField(view_name=sensing_point_view_name)
        field.parent = self
        return {
            point.sensor.pk: field.to_representation(point) for point in
            self.instance.sensing_points.all()
        }

class ResourceLocationRelatedField(HyperlinkedRelatedField):
    def __init__(self, **kwargs):
        super().__init__(DUMMY_VIEW_NAME)

    @property
    def queryset(self):
        # We will never actually read this queryset, but some checks will make
        # sure that is evaluates to True, so just make it True
        return True

    @queryset.setter
    def queryset(self, val):
        # We should never be assigning an actual value to this property
        assert val is None

    @property
    def choices(self):
        res = OrderedDict()
        enclosure = Enclosure.get_solo()
        res[str(self.to_representation(enclosure))] = str(enclosure)
        current_schema = all_schemata[system_layout.current_value]
        for entity in current_schema.dynamic_entities:
            model = dynamic_models[entity]
            for obj in model.objects.all():
                res[str(self.to_representation(obj))] = str(obj)
        for tray in Tray.objects.all():
            res[str(self.to_representation(tray))] = str(tray)
        return res

    def to_internal_value(self, data):
        request = self.context.get('request', None)
        try:
            http_prefix = data.startswith(('http:', 'https:'))
        except AttributeError:
            self.fail('incorrect_type', data_type=type(data).__name__)

        if http_prefix:
            # If needed convert absolute URLs to relative path
            data = urlparse.urlparse(data).path
            prefix = get_script_prefix()
            if data.startswith(prefix):
                data = '/' + data[len(prefix):]

        try:
            match = resolve(data)
        except Resolver404:
            self.fail('no_match')

        try:
            lookup_value = match.kwargs[self.lookup_url_kwarg]
            lookup_kwargs = {self.lookup_field: lookup_value}
            model = match.func.cls.model
            return model.objects.get(**lookup_kwargs)
        except (ObjectDoesNotExist, TypeError, ValueError):
            self.fail('does_not_exist')

    def to_representation(self, value):
        request = self.context.get('request', None)
        format = self.context.get('format', None)

        if format and self.format and self.format != format:
            format = self.format

        view_name = get_detail_view_name(value._meta.model)
        return self.get_url(value, view_name, request, format)

class ResourceSerializer(BaseSerializer):
    class Meta:
        model = Resource
        exclude = ('location_type', 'location_id')
    location = ResourceLocationRelatedField()
