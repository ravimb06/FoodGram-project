from rest_framework.permissions import SAFE_METHODS, BasePermission

from users.models import UserRole


class IsAuthorOrAdminOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or obj.author == request.user
                or request.user.role == UserRole.ADMIN)
