from rest_framework.permissions import BasePermission, SAFE_METHODS

class EnforceReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return not obj.read_only or request.method in SAFE_METHODS
