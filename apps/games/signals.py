from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import GameRoom, GameRound, GameGuess, GameAchievement
from apps.social.models import Notification

@receiver(post_save, sender=GameRoom)
def create_game_room_notification(sender, instance, created, **kwargs):
    """Oyun odası oluşturulduğunda bildirim oluştur"""
    if created:
        # Oyun odasını oluşturan kullanıcının takipçilerine bildir
        for follower in instance.host.followers.all():
            Notification.objects.create(
                user=follower.user,
                type='game',
                title='Yeni Oyun Odası',
                message=f'{instance.host.username} yeni bir oyun odası oluşturdu: {instance.name}',
                related_object_id=instance.id,
                related_object_type='game_room'
            )

@receiver(post_save, sender=GameRound)
def handle_game_round(sender, instance, created, **kwargs):
    """Oyun turu oluşturulduğunda veya güncellendiğinde işlemler"""
    if created:
        # Odadaki tüm oyunculara yeni tur bildirimi gönder
        for player in instance.room.players.all():
            if player != instance.current_player:
                Notification.objects.create(
                    user=player.user,
                    type='game',
                    title='Yeni Oyun Turu',
                    message=f'"{instance.room.name}" odasında yeni tur başladı.',
                    related_object_id=instance.id,
                    related_object_type='game_round'
                )

@receiver(post_save, sender=GameGuess)
def handle_game_guess(sender, instance, created, **kwargs):
    """Oyun tahmini yapıldığında işlemler"""
    if created and instance.is_correct:
        # Doğru tahmin yapıldığında bildirim oluştur
        Notification.objects.create(
            user=instance.round.current_player.user,
            type='game',
            title='Doğru Tahmin',
            message=f'{instance.player.username} doğru tahminde bulundu!',
            related_object_id=instance.id,
            related_object_type='game_guess'
        )

@receiver(post_save, sender=GameAchievement)
def create_achievement_notification(sender, instance, created, **kwargs):
    """Oyun başarımı kazanıldığında bildirim oluştur"""
    if created:
        Notification.objects.create(
            user=instance.user,
            type='achievement',
            title='Yeni Başarım',
            message=f'"{instance.game.name}" oyununda yeni bir başarım kazandınız: {instance.achievement_type}',
            related_object_id=instance.id,
            related_object_type='game_achievement'
        ) 