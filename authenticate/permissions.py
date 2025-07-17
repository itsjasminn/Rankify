from rest_framework.permissions import BasePermission

from authenticate.models import User


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == User.RoleType.Admin)
