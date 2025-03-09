from rest_framework import serializers
from .models import (
    Game, GameRoom, GamePlayer, GameRound,
    GameGuess, GameChat, GameAchievement
)
from apps.accounts.serializers import UserPublicProfileSerializer

class GameSerializer(serializers.ModelSerializer):
    """Oyun serializerı"""
    class Meta:
        model = Game
        fields = (
            'id', 'name', 'description', 'game_type',
            'max_players', 'min_players', 'duration',
            'points', 'is_active'
        )

class GamePlayerSerializer(serializers.ModelSerializer):
    """Oyuncu serializerı"""
    user = UserPublicProfileSerializer(read_only=True)

    class Meta:
        model = GamePlayer
        fields = ('id', 'user', 'score', 'joined_at', 'is_ready', 'is_active')
        read_only_fields = ('joined_at',)

class GameRoomSerializer(serializers.ModelSerializer):
    """Oyun odası serializerı"""
    host = UserPublicProfileSerializer(read_only=True)
    players = GamePlayerSerializer(many=True, read_only=True)
    current_player = serializers.SerializerMethodField()
    game = GameSerializer(read_only=True)
    game_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = GameRoom
        fields = (
            'id', 'game', 'game_id', 'host', 'name', 'status',
            'created_at', 'started_at', 'finished_at',
            'is_private', 'password', 'max_players',
            'players', 'current_player'
        )
        read_only_fields = ('created_at', 'started_at', 'finished_at')
        extra_kwargs = {'password': {'write_only': True}}

    def get_current_player(self, obj):
        current_round = obj.rounds.filter(finished_at__isnull=True).first()
        if current_round:
            return GamePlayerSerializer(current_round.current_player).data
        return None

class GameRoundSerializer(serializers.ModelSerializer):
    """Oyun turu serializerı"""
    current_player = GamePlayerSerializer(read_only=True)
    guesses = serializers.SerializerMethodField()
    drawing_data = serializers.JSONField(required=False)

    class Meta:
        model = GameRound
        fields = (
            'id', 'round_number', 'started_at', 'finished_at',
            'current_player', 'word', 'drawing_data', 'guesses'
        )
        read_only_fields = ('started_at', 'finished_at')

    def get_guesses(self, obj):
        request = self.context.get('request')
        if request and request.user == obj.current_player.user:
            return GameGuessSerializer(obj.guesses.all(), many=True).data
        return GameGuessSerializer(
            obj.guesses.filter(player__user=request.user),
            many=True
        ).data

class GameGuessSerializer(serializers.ModelSerializer):
    """Tahmin serializerı"""
    player = GamePlayerSerializer(read_only=True)

    class Meta:
        model = GameGuess
        fields = (
            'id', 'player', 'guess', 'is_correct',
            'created_at', 'points_earned'
        )
        read_only_fields = ('created_at', 'is_correct', 'points_earned')

class GameChatSerializer(serializers.ModelSerializer):
    """Oyun sohbeti serializerı"""
    player = GamePlayerSerializer(read_only=True)

    class Meta:
        model = GameChat
        fields = ('id', 'player', 'message', 'created_at', 'is_system_message')
        read_only_fields = ('created_at', 'is_system_message')

class GameAchievementSerializer(serializers.ModelSerializer):
    """Oyun başarısı serializerı"""
    user = UserPublicProfileSerializer(read_only=True)
    game = GameSerializer(read_only=True)

    class Meta:
        model = GameAchievement
        fields = ('id', 'user', 'game', 'achievement_type', 'value', 'earned_at')
        read_only_fields = ('earned_at',) 