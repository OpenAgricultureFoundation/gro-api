from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework.permissions import IsAdminUser
from ..gro_api.serializers import BaseSerializer

class UserSerializer(BaseSerializer):
    class Meta:
        model = get_user_model()
        permission_classes = IsAdminUser

class PermissionSerializer(BaseSerializer):
    class Meta:
        model = Permission
