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

class IsDeviceOwner(permissions.BasePermission):
    """
    Cihaz sahibine erişim izni verir.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user 