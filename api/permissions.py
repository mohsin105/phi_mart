# from rest_framework.permissions import BasePermission,SAFE_METHODS
from rest_framework import permissions #entire file is imported to remove crowd from this import section


"""Best Practice"""

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)

"""Basic approach

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method=='GET':
            return True
        return bool(request.user and request.user.is_staff)
"""

class FullDjangoModelPermission(permissions.DjangoModelPermissions):
    def __init__(self):
        self.perms_map['GET']=['%(app_label)s.add_%(model_name)s']