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
