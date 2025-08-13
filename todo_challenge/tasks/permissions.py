from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    """Permite acceso solo al dueño del objeto."""
    def has_object_permission(self, request, view, obj):
        return getattr(obj, 'user_id', None) == getattr(request.user, 'id', None)
