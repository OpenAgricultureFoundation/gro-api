from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from ..data_manager.serializers import BaseSerializer

class UserSerializer(BaseSerializer):
    class Meta:
        model = get_user_model()

class PermissionSerializer(BaseSerializer):
    class Meta:
        model = Permission
