from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from rest_framework.permissions import IsAdminUser
from rest_framework.authtoken.models import Token
from ..gro_api.serializers import BaseSerializer

class UserSerializer(BaseSerializer):
    class Meta:
        model = get_user_model()

class GroupSerializer(BaseSerializer):
    class Meta:
        model = Group

class PermissionSerializer(BaseSerializer):
    class Meta:
        model = Permission

class TokenSerializer(BaseSerializer):
    class Meta:
        model = Token
