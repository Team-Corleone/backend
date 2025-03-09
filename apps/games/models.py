from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User
from apps.movies.models import Movie, Person

class Game(models.Model):
    """Oyun modeli"""
    GAME_TYPES = [
        ('draw_guess', _('Çiz & Tahmin Et')),
        ('actor_movie', _('Aktör & Film')),
        ('movie_quiz', _('Film Bilgi Yarışması')),
        ('movie_puzzle', _('Film Bulmaca')),
    ]
    
    name = models.CharField(_('Oyun Adı'), max_length=255)
    description = models.TextField(_('Açıklama'))
    game_type = models.CharField(_('Oyun Tipi'), max_length=50, choices=GAME_TYPES)
    max_players = models.IntegerField(_('Maksimum Oyuncu'), default=4)
    min_players = models.IntegerField(_('Minimum Oyuncu'), default=2)
    duration = models.IntegerField(_('Süre (dakika)'), default=15)
    points = models.IntegerField(_('Kazanılacak Puan'), default=100)
    is_active = models.BooleanField(_('Aktif'), default=True)
    
    class Meta:
        verbose_name = _('Oyun')
        verbose_name_plural = _('Oyunlar')

class GameRoom(models.Model):
    """Oyun odası"""
    ROOM_STATUS = [
        ('waiting', _('Bekliyor')),
        ('playing', _('Oynanıyor')),
        ('finished', _('Tamamlandı')),
    ]
    
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='rooms')
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_rooms')
    name = models.CharField(_('Oda Adı'), max_length=255)
    status = models.CharField(_('Durum'), max_length=20, choices=ROOM_STATUS, default='waiting')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    is_private = models.BooleanField(_('Özel Oda'), default=False)
    password = models.CharField(_('Şifre'), max_length=50, blank=True)
    max_players = models.IntegerField(_('Maksimum Oyuncu'))
    
    class Meta:
        verbose_name = _('Oyun Odası')
        verbose_name_plural = _('Oyun Odaları')

class GamePlayer(models.Model):
    """Oyun oyuncusu"""
    room = models.ForeignKey(GameRoom, on_delete=models.CASCADE, related_name='players')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_participations')
    score = models.IntegerField(_('Puan'), default=0)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_ready = models.BooleanField(_('Hazır'), default=False)
    is_active = models.BooleanField(_('Aktif'), default=True)
    
    class Meta:
        verbose_name = _('Oyuncu')
        verbose_name_plural = _('Oyuncular')
        unique_together = ('room', 'user')

class GameRound(models.Model):
    """Oyun turu"""
    room = models.ForeignKey(GameRoom, on_delete=models.CASCADE, related_name='rounds')
    round_number = models.IntegerField(_('Tur Numarası'))
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    current_player = models.ForeignKey(GamePlayer, on_delete=models.CASCADE, related_name='active_rounds')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True)
    word = models.CharField(_('Kelime'), max_length=255, blank=True)
    drawing_data = models.JSONField(_('Çizim Verisi'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Oyun Turu')
        verbose_name_plural = _('Oyun Turları')
        ordering = ['round_number']

class GameGuess(models.Model):
    """Oyun tahmini"""
    round = models.ForeignKey(GameRound, on_delete=models.CASCADE, related_name='guesses')
    player = models.ForeignKey(GamePlayer, on_delete=models.CASCADE, related_name='guesses')
    guess = models.CharField(_('Tahmin'), max_length=255)
    is_correct = models.BooleanField(_('Doğru'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    points_earned = models.IntegerField(_('Kazanılan Puan'), default=0)
    
    class Meta:
        verbose_name = _('Tahmin')
        verbose_name_plural = _('Tahminler')
        ordering = ['created_at']

class GameChat(models.Model):
    """Oyun sohbeti"""
    room = models.ForeignKey(GameRoom, on_delete=models.CASCADE, related_name='chat_messages')
    player = models.ForeignKey(GamePlayer, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField(_('Mesaj'))
    created_at = models.DateTimeField(auto_now_add=True)
    is_system_message = models.BooleanField(_('Sistem Mesajı'), default=False)
    
    class Meta:
        verbose_name = _('Sohbet Mesajı')
        verbose_name_plural = _('Sohbet Mesajları')
        ordering = ['created_at']

class GameAchievement(models.Model):
    """Oyun başarıları"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_achievements')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='achievements')
    achievement_type = models.CharField(_('Başarı Tipi'), max_length=50)
    value = models.IntegerField(_('Değer'), default=0)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Oyun Başarısı')
        verbose_name_plural = _('Oyun Başarıları') 