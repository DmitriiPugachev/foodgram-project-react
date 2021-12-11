from rest_framework.permissions import SAFE_METHODS, BasePermission

from users.models import UserRoles


class IsSafeMethod(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == UserRoles.ADMIN

    def has_object_permission(self, request, view, obj):
        return request.user.role == UserRoles.ADMIN


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser


class CustomIsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated
