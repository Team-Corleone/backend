from rest_framework import permissions

class IsGameHost(permissions.BasePermission):
    """
    Oyun odası sahibine erişim izni verir.
    """

    def has_object_permission(self, request, view, obj):
        return obj.host == request.user

class IsRoomPlayer(permissions.BasePermission):
    """
    Oyun odasındaki oyunculara erişim izni verir.
    """

    def has_permission(self, request, view):
        room_pk = view.kwargs.get('room_pk')
        if not room_pk:
            return False
        return request.user.game_participations.filter(room_id=room_pk).exists()

class IsCurrentPlayer(permissions.BasePermission):
    """
    Sırası gelen oyuncuya erişim izni verir.
    """

    def has_object_permission(self, request, view, obj):
        return obj.current_player.user == request.user 