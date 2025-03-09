from rest_framework import generics, status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import (
    Game, GameRoom, GamePlayer, GameRound,
    GameGuess, GameChat, GameAchievement
)
from .serializers import (
    GameSerializer, GameRoomSerializer, GamePlayerSerializer,
    GameRoundSerializer, GameGuessSerializer, GameChatSerializer,
    GameAchievementSerializer
)
from .permissions import IsGameHost, IsRoomPlayer

class GameListView(generics.ListAPIView):
    """Oyun listesi"""
    queryset = Game.objects.filter(is_active=True)
    serializer_class = GameSerializer
    permission_classes = (IsAuthenticated,)

class GameDetailView(generics.RetrieveAPIView):
    """Oyun detayı"""
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = (IsAuthenticated,)

class GameRoomListView(generics.ListAPIView):
    """Oyun odaları listesi"""
    serializer_class = GameRoomSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return GameRoom.objects.filter(status='waiting')

class GameRoomCreateView(generics.CreateAPIView):
    """Oyun odası oluşturma"""
    serializer_class = GameRoomSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        room = serializer.save(host=self.request.user)
        GamePlayer.objects.create(
            room=room,
            user=self.request.user,
            is_ready=True
        )

class GameRoomDetailView(generics.RetrieveAPIView):
    """Oyun odası detayı"""
    queryset = GameRoom.objects.all()
    serializer_class = GameRoomSerializer
    permission_classes = (IsAuthenticated,)

class JoinRoomView(views.APIView):
    """Oyun odasına katılma"""
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        try:
            room = GameRoom.objects.get(pk=pk, status='waiting')
            if room.players.count() >= room.max_players:
                return Response(
                    {'detail': 'Oda dolu.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if room.is_private and request.data.get('password') != room.password:
                return Response(
                    {'detail': 'Yanlış şifre.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            GamePlayer.objects.create(room=room, user=request.user)
            return Response({'detail': 'Odaya katıldınız.'})
        except GameRoom.DoesNotExist:
            return Response(
                {'detail': 'Oda bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )

class LeaveRoomView(views.APIView):
    """Oyun odasından ayrılma"""
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        try:
            player = GamePlayer.objects.get(
                room_id=pk,
                user=request.user,
                room__status='waiting'
            )
            if player.room.host == request.user:
                player.room.delete()
                return Response({'detail': 'Oda kapatıldı.'})
            player.delete()
            return Response({'detail': 'Odadan ayrıldınız.'})
        except GamePlayer.DoesNotExist:
            return Response(
                {'detail': 'Oyuncu bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )

class StartGameView(views.APIView):
    """Oyunu başlatma"""
    permission_classes = (IsAuthenticated, IsGameHost)

    def post(self, request, pk):
        try:
            room = GameRoom.objects.get(pk=pk, status='waiting')
            if room.players.count() < room.game.min_players:
                return Response(
                    {'detail': 'Yetersiz oyuncu sayısı.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not all(player.is_ready for player in room.players.all()):
                return Response(
                    {'detail': 'Tüm oyuncular hazır değil.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            room.status = 'playing'
            room.started_at = timezone.now()
            room.save()
            
            # İlk turu oluştur
            current_player = room.players.first()
            GameRound.objects.create(
                room=room,
                round_number=1,
                current_player=current_player
            )
            
            # WebSocket ile oyunculara bildir
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'room_{room.id}',
                {
                    'type': 'game_started',
                    'message': 'Oyun başladı!'
                }
            )
            return Response({'detail': 'Oyun başladı.'})
        except GameRoom.DoesNotExist:
            return Response(
                {'detail': 'Oda bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )

class EndGameView(views.APIView):
    """Oyunu bitirme"""
    permission_classes = (IsAuthenticated, IsGameHost)

    def post(self, request, pk):
        try:
            room = GameRoom.objects.get(pk=pk, status='playing')
            room.status = 'finished'
            room.finished_at = timezone.now()
            room.save()
            
            # Kazananı belirle
            winner = room.players.order_by('-score').first()
            
            # WebSocket ile oyunculara bildir
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'room_{room.id}',
                {
                    'type': 'game_ended',
                    'message': f'Oyun bitti! Kazanan: {winner.user.username}'
                }
            )
            return Response({
                'detail': 'Oyun bitti.',
                'winner': winner.user.username,
                'score': winner.score
            })
        except GameRoom.DoesNotExist:
            return Response(
                {'detail': 'Oda bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )

class GameRoundListView(generics.ListAPIView):
    """Oyun turları listesi"""
    serializer_class = GameRoundSerializer
    permission_classes = (IsAuthenticated, IsRoomPlayer)

    def get_queryset(self):
        return GameRound.objects.filter(room_id=self.kwargs['room_pk'])

class CurrentRoundView(generics.RetrieveAPIView):
    """Mevcut tur bilgisi"""
    serializer_class = GameRoundSerializer
    permission_classes = (IsAuthenticated, IsRoomPlayer)

    def get_object(self):
        return GameRound.objects.filter(
            room_id=self.kwargs['room_pk'],
            finished_at__isnull=True
        ).first()

class SubmitGuessView(views.APIView):
    """Tahmin gönderme"""
    permission_classes = (IsAuthenticated, IsRoomPlayer)

    def post(self, request, pk):
        try:
            round = GameRound.objects.get(pk=pk, finished_at__isnull=True)
            player = GamePlayer.objects.get(
                room=round.room,
                user=request.user
            )
            
            guess = request.data.get('guess', '').lower().strip()
            correct_answer = round.word.lower().strip()
            
            is_correct = guess == correct_answer
            points_earned = 100 if is_correct else 0
            
            GameGuess.objects.create(
                round=round,
                player=player,
                guess=guess,
                is_correct=is_correct,
                points_earned=points_earned
            )
            
            if is_correct:
                player.score += points_earned
                player.save()
                
                # Turu bitir ve yeni tur başlat
                round.finished_at = timezone.now()
                round.save()
                
                next_player = round.room.players.exclude(
                    id=round.current_player.id
                ).first()
                
                if next_player:
                    GameRound.objects.create(
                        room=round.room,
                        round_number=round.round_number + 1,
                        current_player=next_player
                    )
            
            return Response({
                'detail': 'Doğru tahmin!' if is_correct else 'Yanlış tahmin.',
                'points_earned': points_earned
            })
        except (GameRound.DoesNotExist, GamePlayer.DoesNotExist):
            return Response(
                {'detail': 'Tur veya oyuncu bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )

class SubmitDrawingView(views.APIView):
    """Çizim gönderme"""
    permission_classes = (IsAuthenticated, IsRoomPlayer)

    def post(self, request, pk):
        try:
            round = GameRound.objects.get(
                pk=pk,
                finished_at__isnull=True,
                current_player__user=request.user
            )
            round.drawing_data = request.data.get('drawing_data')
            round.save()
            
            # WebSocket ile diğer oyunculara bildir
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'room_{round.room.id}',
                {
                    'type': 'drawing_updated',
                    'drawing_data': round.drawing_data
                }
            )
            return Response({'detail': 'Çizim güncellendi.'})
        except GameRound.DoesNotExist:
            return Response(
                {'detail': 'Tur bulunamadı veya sıra sizde değil.'},
                status=status.HTTP_404_NOT_FOUND
            )

class GameChatView(generics.CreateAPIView):
    """Oyun sohbeti mesaj gönderme"""
    serializer_class = GameChatSerializer
    permission_classes = (IsAuthenticated, IsRoomPlayer)

    def perform_create(self, serializer):
        player = GamePlayer.objects.get(
            room_id=self.kwargs['room_pk'],
            user=self.request.user
        )
        serializer.save(player=player)

class ChatHistoryView(generics.ListAPIView):
    """Sohbet geçmişi"""
    serializer_class = GameChatSerializer
    permission_classes = (IsAuthenticated, IsRoomPlayer)

    def get_queryset(self):
        return GameChat.objects.filter(
            room_id=self.kwargs['room_pk']
        ).order_by('-created_at')[:50]

class GamePlayerListView(generics.ListAPIView):
    """Oyun oyuncuları listesi"""
    serializer_class = GamePlayerSerializer
    permission_classes = (IsAuthenticated, IsRoomPlayer)

    def get_queryset(self):
        return GamePlayer.objects.filter(
            room_id=self.kwargs['room_pk']
        ).order_by('-score')

class PlayerReadyView(views.APIView):
    """Oyuncu hazır durumu"""
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        try:
            player = GamePlayer.objects.get(
                pk=pk,
                user=request.user,
                room__status='waiting'
            )
            player.is_ready = not player.is_ready
            player.save()
            return Response({
                'detail': 'Hazır durumu güncellendi.',
                'is_ready': player.is_ready
            })
        except GamePlayer.DoesNotExist:
            return Response(
                {'detail': 'Oyuncu bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )

class KickPlayerView(views.APIView):
    """Oyuncu atma"""
    permission_classes = (IsAuthenticated, IsGameHost)

    def post(self, request, pk):
        try:
            player = GamePlayer.objects.get(
                pk=pk,
                room__status='waiting'
            )
            if player.user == request.user:
                return Response(
                    {'detail': 'Kendinizi atamazsınız.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            player.delete()
            return Response({'detail': 'Oyuncu atıldı.'})
        except GamePlayer.DoesNotExist:
            return Response(
                {'detail': 'Oyuncu bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )

class GameAchievementListView(generics.ListAPIView):
    """Oyun başarıları listesi"""
    serializer_class = GameAchievementSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return GameAchievement.objects.filter(user=self.request.user)

class GameAchievementDetailView(generics.RetrieveAPIView):
    """Oyun başarısı detayı"""
    queryset = GameAchievement.objects.all()
    serializer_class = GameAchievementSerializer
    permission_classes = (IsAuthenticated,)

class PlayerStatsView(views.APIView):
    """Oyuncu istatistikleri"""
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        stats = {
            'total_games': GamePlayer.objects.filter(user=request.user).count(),
            'total_wins': GamePlayer.objects.filter(
                user=request.user,
                room__status='finished'
            ).filter(score=models.Max('score')).count(),
            'total_points': GamePlayer.objects.filter(
                user=request.user
            ).aggregate(total_points=models.Sum('score'))['total_points'] or 0,
            'correct_guesses': GameGuess.objects.filter(
                player__user=request.user,
                is_correct=True
            ).count()
        }
        return Response(stats)

class LeaderboardView(generics.ListAPIView):
    """Liderlik tablosu"""
    serializer_class = GamePlayerSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return GamePlayer.objects.filter(
            room__status='finished'
        ).order_by('-score')[:100] 