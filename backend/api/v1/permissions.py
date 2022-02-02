"""API v.1 custom permissions."""


from rest_framework.permissions import SAFE_METHODS, BasePermission

from users.models import UserRoles


class IsSafeMethod(BasePermission):
    """Custom permission for GET method only."""
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS


class IsOwner(BasePermission):
    """Custom permission for an author of an object only."""
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsAdmin(BasePermission):
    """Custom permission for an admin only."""
    def has_permission(self, request, view):
        return request.user.role == UserRoles.ADMIN

    def has_object_permission(self, request, view, obj):
        return request.user.role == UserRoles.ADMIN


class IsSuperUser(BasePermission):
    """Custom permission for a superuser only."""
    def has_permission(self, request, view):
        return request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser


class CustomIsAuthenticated(BasePermission):
    """Custom permission for an authenticated user only."""
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated
