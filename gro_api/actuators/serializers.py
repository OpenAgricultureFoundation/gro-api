from rest_framework import serializers
from ..gro_api.serializers import BaseSerializer
from .models import (
    ActuatorType, ControlProfile, ActuatorEffect, Actuator, ActuatorState
)


class ActuatorTypeSerializer(BaseSerializer):
    class Meta:
        model = ActuatorType

    def validate(self, data):
        effect = data['resource_effect']
        for property in data['properties']:
            if property.resource_type != effect.resource_type:
                raise serializers.ValidationError(
                    'Proposed actuator type affects properties of a resource '
                    'type other than the one that it is to be installed in.'
                )
        return data


class ActuatorEffectSerializer(BaseSerializer):
    class Meta:
        model = ActuatorEffect

    def validate(self, data):
        correct_type = data['control_profile'].actuator_type.resource_effect.resource_type
        if data['property'].resource_type != correct_type:
            raise serializers.ValidationError(
                'An actuator cannot affect a property on a resource type '
                'than the one it affects.'
            )
        return data


class ControlProfileSerializer(BaseSerializer):
    class Meta:
        model = ControlProfile
        exclude = ('properties',)

    effects = ActuatorEffectSerializer(many=True, read_only=True)

    def create(self, validated_data):
        actuator_type = validated_data['actuator_type']
        instance = super().create(validated_data)
        try:
            for property in actuator_type.properties.all():
                ActuatorEffect.objects.create(
                    control_profile=instance, property=property
                )
        except:
            instance.delete()
            raise
        return instance


class ActuatorSerializer(BaseSerializer):
    class Meta:
        model = Actuator

    index = serializers.ReadOnlyField()
    override_value = serializers.SerializerMethodField()

    def validate(self, data):
        if data['control_profile'].actuator_type != data['actuator_type']:
            raise serializers.ValidationError(
                'Selected control profile does not work for the selected '
                'actuator type.'
            )
        correct_type = data['actuator_type'].resource_effect.resource_type
        if data['resource'].resource_type != correct_type:
            raise serializers.ValidationError(
                'Attempted to install a {} actuator in a {} resource'.format(
                    data['actuator_type'].resource_effect.resource_type,
                    data['resource'].resource_type
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
        actuator_type = validated_data.get(
            'actuator_type', instance.actuator_type
        )
        if actuator_type != instance.actuator_type:
            raise serializers.ValidationError(
                'Changing the type of an existing actuator is not allowed'
            )
        return super().update(instance, validated_data)

    def get_override_value(self, obj):
        return obj.current_override and obj.current_override.value

    def get_unique_together_validators(self):
        # The default unique together validators will try to force `index` to
        # be required, so we have to silence them
        return []


class ActuatorStateSerializer(BaseSerializer):
    class Meta:
        model = ActuatorState
