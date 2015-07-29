from cityfarm_api.serializers import BaseSerializer

from .models import Sensor, SensingPoint

class SensorSerializer(BaseSerializer):
    class Meta:
        model = Sensor

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

