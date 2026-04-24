from rest_framework.permissions import BasePermission, SAFE_METHODS


class RepairActionPermission(BasePermission):
    """
    Lecture : tout utilisateur authentifié
    Écriture : ADMIN ou REPAIR_TECHNICIAN uniquement
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return user.role in ["ADMIN", "REPAIR_TECHNICIAN"]