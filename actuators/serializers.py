from collections import OrderedDict
from rest_framework.fields import ChoiceField
from rest_framework.serializers import ValidationError, ReadOnlyField
from cityfarm_api.serializers import BaseSerializer
from .models import (
    ActuatorCode, ActuatorType, ControlProfile, ActuatorEffect, Actuator
)


class CodeChoiceField(ChoiceField):
    def __init__(self, *args, **kwargs):
        super(ChoiceField, self).__init__(*args, **kwargs)

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value

    @property
    def choices(self):
        return OrderedDict([
            (code.val, code.val) for code in ActuatorCode.objects.all()
        ])


class ActuatorTypeSerializer(BaseSerializer):
    class Meta:
        model = ActuatorType

    code = CodeChoiceField()

    def validate_code(self, val):
        if not len(val) == 2:
            raise ValidationError(
                'ActuatorType codes must be exactly 2 characters long'
            )
        return val

    def validate(self, data):
        resource_type = data['resource_type']
        properties = data['properties']
        for property in properties:
            if property.resource_type != resource_type:
                raise ValidationError(
                    'Proposed actuator type measures properties of a resource '
                    'type other than the one it claims to affect'
                )
        return data


class ActuatorEffectSerializer(BaseSerializer):
    class Meta:
        model = ActuatorEffect


class ControlProfileSerializer(BaseSerializer):
    class Meta:
        model = ControlProfile
        exclude = ('properties',)

    effects = ActuatorEffectSerializer(many=True, read_only=True)


class ActuatorSerializer(BaseSerializer):
    class Meta:
        model = Actuator

    index = ReadOnlyField(default=0)
    override_value = ReadOnlyField()
    override_timeout = ReadOnlyField()

    def validate(self, data):
        actuator_type = data['actuator_type']
        resource = data['resource']
        if actuator_type.resource_type != resource.resource_type:
            raise ValidationError(
                'Attempted to install a {} actuator in a {} resource'.format(
                    actuator_type.resource_type, resource.resource_type
                )
            )
        return data

    def create(self, validated_data):
        actuator_type = validated_data['actuator_type']
        actuator_type.actuator_count += 1
        validated_data['index'] = actuator_type.actuator_count
        if not validated_data.get('name', None):
            validated_data['name'] = "{} Instance {}".format(
                actuator_type.name, validated_data['index']
            )
        instance = super().create(validated_data)
        actuator_type.save()
        return instance

    def update(self, instance, validated_data):
        if validated_data.get('actuator_type', instance.actuator_type) != \
                instance.actuator_type:
            raise ValidationError(
                'Changing the type of an existing actuator is not allowed'
            )
        return super().update(instance, validated_data)
