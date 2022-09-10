from rest_framework import permissions


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    '''
    Allows to modify only to owners or admin users.
    '''

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_staff
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allows to modify only to admin users.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS or request.user.is_staff
        )
