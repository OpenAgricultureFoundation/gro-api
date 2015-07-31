from rest_framework.serializers import ValidationError
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

    def create_points(self, instance):
        for resource_property in instance.sensor_type.properties.all():
            point = SensingPoint(sensor=instance, property=resource_property)
            point.save()

    def clear_points(self, instance):
        for point in instance.sensing_points.all():
            point.delete()

    def create(self, validated_data):
        instance = super().create(validated_data)
        self.create_points(instance)
        return instance

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        if 'sensor_type' in validated_data and \
                validated_data['sensor_type'] != instance.sensor_type:
            self.clear_points(instance)
            instance.sensor_type = validated_data['sensor_type']
            self.create_points(instance)
        instance.resource = validated_data.get('resource', instance.resource)
        instance.save()
        return instance
