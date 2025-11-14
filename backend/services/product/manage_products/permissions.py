# manage_products/permissions.py
from rest_framework.permissions import BasePermission

class IsAuthenticatedCustom(BasePermission):
    """
    Vérifie que le JWT a été validé par le middleware
    et que user_id est présent.
    """
    def has_permission(self, request, view):
        # Le middleware a-t-il ajouté jwt_payload ?
        return hasattr(request, 'jwt_payload') and request.jwt_payload.get('user_id') is not None

    def has_object_permission(self, request, view, obj):
        # Optionnel : contrôle plus fin (ex: propriétaire)
        return True