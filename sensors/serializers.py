from rest_framework.serializers import ValidationError, ReadOnlyField
from rest_framework.exceptions import APIException
from cityfarm_api.serializers import BaseSerializer
from .models import SensorType, Sensor, SensingPoint


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
                'is_active': True
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
        sensor = data['sensor']
        property = data['property']
        if property not in sensor.sensor_type.properties:
            raise ValidationError(
                'Attempted to create a sensor point for a property that it\'s '
                'parent sensor does not measure'
            )
        return data

    def create(self, validated_data):
        property = validated_data['property']
        property.sensing_point_count += 1
        validated_data['index'] = property.sensing_point_count
        instance = super().create(validated_data)
        property.save()
