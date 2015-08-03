from rest_framework.serializers import ValidationError
from cityfarm_api.serializers import BaseSerializer
from .models import ActuatorType, Actuator

class ActuatorTypeSerializer(BaseSerializer):
    class Meta:
        model = ActuatorType

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

class ActuatorSerializer(BaseSerializer):
    class Meta:
        model = Actuator

    def validate(self, data):
        actuator_type = data['actuator_type']
        resource = data['resource']
        if actuator_type.resource_type != resource.resource_type:
            raise ValidationError(
                'Attempted to install a {} actuator in a {} resource'.format(
                    actuator_type.resource_type, resource.resource_Type
                )
            )
        return data
