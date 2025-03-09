import django_filters
from .models import Game, GameRoom

class GameFilter(django_filters.FilterSet):
    """Oyun filtreleme"""
    name = django_filters.CharFilter(lookup_expr='icontains')
    game_type = django_filters.ChoiceFilter(choices=Game.GAME_TYPES)
    min_players = django_filters.NumberFilter(lookup_expr='gte')
    max_players = django_filters.NumberFilter(lookup_expr='lte')
    duration = django_filters.NumberFilter()
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Game
        fields = ['name', 'game_type', 'min_players', 'max_players', 'duration', 'is_active']

class GameRoomFilter(django_filters.FilterSet):
    """Oyun odası filtreleme"""
    name = django_filters.CharFilter(lookup_expr='icontains')
    game = django_filters.NumberFilter()
    status = django_filters.ChoiceFilter(choices=GameRoom.ROOM_STATUS)
    is_private = django_filters.BooleanFilter()
    host = django_filters.NumberFilter(field_name='host__id')
    max_players = django_filters.NumberFilter()

    class Meta:
        model = GameRoom
        fields = ['name', 'game', 'status', 'is_private', 'host', 'max_players'] 