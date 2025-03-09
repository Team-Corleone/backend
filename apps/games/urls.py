from django.urls import path
from . import views
from . import consumers

app_name = 'games'

urlpatterns = [
    # Oyun işlemleri
    path('', views.GameListView.as_view(), name='game_list'),
    path('<int:pk>/', views.GameDetailView.as_view(), name='game_detail'),
    
    # Oyun odaları
    path('rooms/', views.GameRoomListView.as_view(), name='room_list'),
    path('rooms/create/', views.GameRoomCreateView.as_view(), name='create_room'),
    path('rooms/<int:pk>/', views.GameRoomDetailView.as_view(), name='room_detail'),
    path('rooms/<int:pk>/join/', views.JoinRoomView.as_view(), name='join_room'),
    path('rooms/<int:pk>/leave/', views.LeaveRoomView.as_view(), name='leave_room'),
    path('rooms/<int:pk>/start/', views.StartGameView.as_view(), name='start_game'),
    path('rooms/<int:pk>/end/', views.EndGameView.as_view(), name='end_game'),
    
    # Oyun turu işlemleri
    path('rooms/<int:room_pk>/rounds/', views.GameRoundListView.as_view(), name='round_list'),
    path('rooms/<int:room_pk>/current-round/', views.CurrentRoundView.as_view(), name='current_round'),
    path('rounds/<int:pk>/guess/', views.SubmitGuessView.as_view(), name='submit_guess'),
    path('rounds/<int:pk>/drawing/', views.SubmitDrawingView.as_view(), name='submit_drawing'),
    
    # Oyuncu işlemleri
    path('rooms/<int:room_pk>/players/', views.GamePlayerListView.as_view(), name='player_list'),
    path('players/<int:pk>/ready/', views.PlayerReadyView.as_view(), name='player_ready'),
    path('players/<int:pk>/kick/', views.KickPlayerView.as_view(), name='kick_player'),
    
    # Sohbet işlemleri
    path('rooms/<int:room_pk>/chat/', views.GameChatView.as_view(), name='chat'),
    path('rooms/<int:room_pk>/chat/history/', views.ChatHistoryView.as_view(), name='chat_history'),
    
    # Başarılar
    path('achievements/', views.GameAchievementListView.as_view(), name='achievement_list'),
    path('achievements/<int:pk>/', views.GameAchievementDetailView.as_view(), name='achievement_detail'),
    
    # İstatistikler
    path('stats/', views.PlayerStatsView.as_view(), name='player_stats'),
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
]

# WebSocket URL desenleri
websocket_urlpatterns = [
    path('ws/rooms/<int:room_pk>/', consumers.GameRoomConsumer.as_asgi(), name='room_ws'),
] 