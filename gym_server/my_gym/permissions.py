from rest_framework.permissions import BasePermission


class ClientOnly(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.role == 1
                and request.user.is_active)


class StaffOnly(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.role == 2
                and request.user.is_active)
