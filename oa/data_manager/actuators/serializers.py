from rest_framework.serializers import ValidationError, ReadOnlyField
from ..data_manager.serializers import BaseSerializer
from .models import (
    ActuatorClass, ActuatorType, ControlProfile, ActuatorEffect, Actuator,
    ActuatorState
)


class ActuatorClassSerializer(BaseSerializer):
    class Meta:
        model = ActuatorClass


class ActuatorTypeSerializer(BaseSerializer):
    class Meta:
        model = ActuatorType

    def validate_properties_with_class(self, properties, actuator_class):
        for property in properties:
            if property.resource_type != actuator_class.resource_type:
                raise ValidationError(
                    'Proposed actuator type affects properties of a resource '
                    'type other than the one that it is to be installed in.'
                )

    def create(self, validated_data):
        actuator_class = validated_data['actuator_class']
        properties = validated_data['properties']
        self.validate_properties_with_class(properties, actuator_class)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        actuator_class = validated_data.get(
            'actuator_class', instance.actuator_class
        )
        properties = validated_data.get('properties', instance.properties)
        self.validate_properties_with_class(properties, actuator_class)
        return super().update(instance, validated_data)


class ActuatorEffectSerializer(BaseSerializer):
    class Meta:
        model = ActuatorEffect

    def validate_property_with_profile(self, property, profile):
        correct_type = profile.actuator_type.actuator_class.resource_type
        if property.resource_type != correct_type:
            raise ValidationError(
                'An actuator cannot affect a property on a resource type '
                'than the one it affects.'
            )

    def create(self, validated_data):
        property = validated_data['property']
        profile = validated_data['control_profile']
        self.validate_property_with_profile(property, profile)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        property = validated_data.get('property', instance.property)
        profile = validated_data.get(
            'control_profile', instance.control_profile
        )
        self.validate_property_with_profile(property, profile)
        return super().update(instance, validated_data)


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

    index = ReadOnlyField(default=0)
    override_value = ReadOnlyField()
    override_timeout = ReadOnlyField()

    def validate_resource_with_type(self, resource, actuator_type):
        if actuator_type.actuator_class.resource_type != resource.resource_type:
            raise ValidationError(
                'Attempted to install a {} actuator in a {} resource'.format(
                    actuator_type.resource_type, resource.resource_type
                )
            )

    def validate_profile_with_type(self, control_profile, actuator_type):
        if control_profile.actuator_type != actuator_type:
            raise ValidationError(
                'Selected control profile does not work for the selected '
                'actuator type.'
            )

    def create(self, validated_data):
        resource = validated_data['resource']
        actuator_type = validated_data['actuator_type']
        control_profile = validated_data['control_profile']
        self.validate_resource_with_type(resource, actuator_type)
        self.validate_profile_with_type(control_profile, actuator_type)
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
        resource = validated_data.get('resource', instance.resource)
        actuator_type = validated_data.get(
            'actuator_type', instance.actuator_type
        )
        control_profile = validated_data.get(
            'control_profile', instance.control_profile
        )
        self.validate_resource_with_type(resource, actuator_type)
        self.validate_profile_with_type(control_profile, actuator_type)
        if actuator_type != instance.actuator_type:
            raise ValidationError(
                'Changing the type of an existing actuator is not allowed'
            )
        return super().update(instance, validated_data)


class ActuatorStateSerializer(BaseSerializer):
    class Meta:
        model = ActuatorState
