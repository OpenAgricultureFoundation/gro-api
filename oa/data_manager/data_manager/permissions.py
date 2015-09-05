from rest_framework.permissions import (
    BasePermission, SAFE_METHODS
)

class IsAdminOrReadOnly(BasePermission):
    """
    Allow write access only to admin users and read access to everyone
    """
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or request.user and
            request.user.is_staff
        )

class EnforceReadOnly(BasePermission):
    """
    If the read-only field on the object being called is set to true, make the
    request read-only
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        else:
            return not obj.read_only
