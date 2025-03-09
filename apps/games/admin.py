from django.contrib import admin
from .models import (
    Game, GameRoom, GamePlayer, GameRound,
    GameGuess, GameChat, GameAchievement
)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'game_type', 'max_players', 'duration', 'is_active')
    list_filter = ('game_type', 'is_active')
    search_fields = ('name',)

@admin.register(GameRoom)
class GameRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'game', 'host', 'status', 'created_at', 'is_private')
    list_filter = ('status', 'game', 'is_private')
    search_fields = ('name', 'host__username')

@admin.register(GamePlayer)
class GamePlayerAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'score', 'is_ready', 'is_active')
    list_filter = ('is_ready', 'is_active')
    search_fields = ('user__username', 'room__name')

@admin.register(GameRound)
class GameRoundAdmin(admin.ModelAdmin):
    list_display = ('room', 'round_number', 'current_player', 'started_at', 'finished_at')
    list_filter = ('room',)
    search_fields = ('room__name', 'current_player__user__username')

@admin.register(GameGuess)
class GameGuessAdmin(admin.ModelAdmin):
    list_display = ('round', 'player', 'guess', 'is_correct', 'points_earned')
    list_filter = ('is_correct',)
    search_fields = ('player__user__username', 'guess')

@admin.register(GameChat)
class GameChatAdmin(admin.ModelAdmin):
    list_display = ('room', 'player', 'message', 'created_at', 'is_system_message')
    list_filter = ('is_system_message',)
    search_fields = ('player__user__username', 'message')

@admin.register(GameAchievement)
class GameAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'achievement_type', 'value', 'earned_at')
    list_filter = ('game', 'achievement_type')
    search_fields = ('user__username',) 