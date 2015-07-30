from rest_framework.serializer import ValidationError
from cityfarm_api.serializers import BaseSerializer
from .models import ResourceType, ResourceProperty

class ResourceTypeSerializer(BaseSerializer):
    class Meta:
        model = ResourceType

    def validate_read_only(self, value):
        if value:
            raise ValidationError(
                'This object is read-only and cannot be modified'
            )
