from rest_framework.fields import SkipField
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.serializers import ValidationError, ReadOnlyField
from ..data_manager.serializers import BaseSerializer
from .models import SensorType, Sensor, SensingPoint, DataPoint


class SensorTypeSerializer(BaseSerializer):
    class Meta:
        model = SensorType

    def validate(self, data):
        resource_type = data['resource_type']
        properties = data['properties']
        for property in properties:
            if property.resource_type != resource_type:
                raise ValidationError(
                    'Proposed sensor type measures properties of a resource '
                    'type other than the one is claims to monitor'
                )
        return data


class SensorSerializer(BaseSerializer):
    class Meta:
        model = Sensor

    index = ReadOnlyField()

    def validate(self, data):
        sensor_type = data['sensor_type']
        resource = data['resource']
        if sensor_type.resource_type != resource.resource_type:
            raise ValidationError(
                'Attempted to install a {} sensor in a {} resource'.format(
                    sensor_type.resource_type, resource.resource_type
                )
            )
        return data

    def create(self, validated_data):
        sensor_type = validated_data['sensor_type']
        sensor_type.sensor_count += 1
        validated_data['index'] = sensor_type.sensor_count
        if not validated_data.get('name', None):
            validated_data['name'] = "{} Instance {}".format(
                sensor_type.name, validated_data['index']
            )
        instance = super().create(validated_data)
        sensor_type.save()
        serializer = SensingPointSerializer()
        for resource_property in instance.sensor_type.properties.all():
            serializer.create({
                'sensor': instance, 'property': resource_property,
                'is_active': True, 'is_pseudo': False, 'auto_created': True
            })
        return instance

    def update(self, instance, validated_data):
        if validated_data.get('sensor_type', instance.sensor_type) != \
                instance.sensor_type:
            raise ValidationError(
                'Changing the type of an existing sensor is not allowed'
            )
        return super().update(instance, validated_data)

    def get_unique_together_validators(self):
        # The default unique together validators will try to force `index` to
        # be required, so we have to silence them
        return []


class SensingPointSerializer(BaseSerializer):
    class Meta:
        model = SensingPoint

    index = ReadOnlyField()

    def validate(self, data):
        sensor = data.get('sensor', None)
        property = data.get('property', None)
        if sensor and property and \
                property not in sensor.sensor_type.properties.all():
            raise ValidationError(
                'Attempted to create a sensing point for a property that it\'s '
                'parent sensor does not measure'
            )
        is_pseudo = data.get('is_pseudo', None)
        if is_pseudo and sensor:
            raise ValidationError(
                'Installing a pseudo sensing point in a real sensor is not '
                'allowed.'
            )
        return data

    def create(self, validated_data):
        property = validated_data['property']
        property.sensing_point_count += 1
        validated_data['index'] = property.sensing_point_count
        instance = super().create(validated_data)
        property.save()
        return instance

    def update(self, instance, validated_data):
        if instance.auto_created:
            new_sensor = validated_data.get('sensor', instance.sensor)
            new_property = validated_data.get('property', instance.property)
            if new_sensor != instance.sensor:
                raise ValidationError(
                    'This sensing point was automatically generated. Moving '
                    'it to a different sensor is not allowed.'
                )
            if new_property != instance.property:
                raise ValidationError(
                    'This sensing point was automatically generated. Changing '
                    'the property that is measures is not allowed.'
                )
        return super().update(instance, validated_data)


class OptionalHyperlinkedIdentityField(HyperlinkedIdentityField):
    def get_attribute(self, instance):
        try:
            instance.pk
        except AttributeError:
            raise SkipField()
        return super().get_attribute(instance)


class DataPointSerializer(BaseSerializer):
    class Meta:
        model = DataPoint

    serializer_url_field = OptionalHyperlinkedIdentityField
