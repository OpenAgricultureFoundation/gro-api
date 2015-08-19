from urllib.parse import urlparse
from collections import OrderedDict
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import get_script_prefix, resolve, Resolver404
from rest_framework.relations import HyperlinkedRelatedField
from rest_framework.serializers import ReadOnlyField, ValidationError
from rest_framework.utils.field_mapping import get_detail_view_name
from ..data_manager.utils import system_layout
from ..data_manager.serializers import BaseSerializer, DUMMY_VIEW_NAME
from ..layout.models import Enclosure, Tray, dynamic_models
from ..layout.schemata import all_schemata
from .models import ResourceType, ResourceProperty, ResourceEffect, Resource


class ResourceTypeSerializer(BaseSerializer):
    class Meta:
        model = ResourceType

    def validate_code(self, val):
        if not len(val) == 1:
            raise ValidationError(
                'ResourceType codes must be exactly 1 character long'
            )
        return val


class ResourcePropertySerializer(BaseSerializer):
    class Meta:
        model = ResourceProperty
        exclude = ('controlprofile_set',)

    def validate_code(self, val):
        if not len(val) == 2:
            raise ValidationError(
                'ResourceProperty codes must be exactly 2 characters long'
            )
        return val

    def validate(self, data):
        min_operating_value = data.get('min_operating_value', None)
        max_operating_value = data.get('max_operating_value', None)
        if min_operating_value and max_operating_value and \
                min_operating_value > max_operating_value:
            raise ValidationError(
                'Maximum operating value must be greater than minimum '
                'operating value.'
            )
        return data


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
        for entity_name in current_schema.dynamic_entities:
            model = dynamic_models[entity_name]
            for obj in model.objects.all():
                res[str(self.to_representation(obj))] = str(obj)
        for tray in Tray.objects.all():
            res[str(self.to_representation(tray))] = str(tray)
        return res

    def to_internal_value(self, data):
        try:
            http_prefix = data.startswith(('http:', 'https:'))
        except AttributeError:
            self.fail('incorrect_type', data_type=type(data).__name__)

        if http_prefix:
            # If needed convert absolute URLs to relative path
            data = urlparse(data).path
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


class ResourceEffectSerializer(BaseSerializer):
    class Meta:
        model = ResourceEffect


class ResourceSerializer(BaseSerializer):
    class Meta:
        model = Resource
        exclude = ('location_type', 'location_id')

    index = ReadOnlyField()
    location = ResourceLocationRelatedField()

    def create(self, validated_data):
        resource_type = validated_data['resource_type']
        resource_type.resource_count += 1
        validated_data['index'] = resource_type.resource_count
        if not validated_data.get('name', None):
            validated_data['name'] = "{} Resource {}".format(
                resource_type.name, validated_data['index']
            )
        instance = super().create(validated_data)
        resource_type.save()
        return instance

    def update(self, instance, validated_data):
        if validated_data.get('resource_type', instance.resource_type) != \
                instance.resource_type:
            raise ValidationError(
                'Changing the type of an existing resource is not allowed'
            )
        return super().update(instance, validated_data)

    def get_unique_together_validators(self):
        # The default unique together validators will try to force `index` to
        # be required, so we have to silence them
        return []
