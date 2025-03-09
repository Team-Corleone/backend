from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Nesne sahibine düzenleme izni verir.
    Diğer kullanıcılar sadece görüntüleyebilir.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class IsListOwnerOrReadOnly(permissions.BasePermission):
    """
    Liste sahibine düzenleme izni verir.
    Diğer kullanıcılar sadece görüntüleyebilir.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.is_public or obj.user == request.user
        return obj.user == request.user

class IsRatingOwnerOrReadOnly(permissions.BasePermission):
    """
    Değerlendirme sahibine düzenleme izni verir.
    Diğer kullanıcılar sadece görüntüleyebilir.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user 