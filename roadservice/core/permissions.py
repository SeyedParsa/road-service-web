from rest_framework import permissions

from accounts.models import Role


class IsCitizen(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.has_role() and user.role.type == Role.Type.CITIZEN


class IsServiceman(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.has_role() and user.role.type == Role.Type.SERVICEMAN


class IsCountyExpert(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.has_role() and user.role.type == Role.Type.COUNTY_EXPERT
