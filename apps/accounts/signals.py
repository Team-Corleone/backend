from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserFollowing, UserBlock, UserAchievement
from apps.social.models import Notification

User = get_user_model()

@receiver(post_save, sender=UserFollowing)
def create_follow_notification(sender, instance, created, **kwargs):
    """Takip edildiğinde bildirim oluştur"""
    if created:
        Notification.objects.create(
            user=instance.following_user,
            type='follow',
            title='Yeni Takipçi',
            message=f'{instance.user.username} sizi takip etmeye başladı.',
            related_object_id=instance.user.id,
            related_object_type='user'
        )

@receiver(post_delete, sender=UserFollowing)
def create_unfollow_notification(sender, instance, **kwargs):
    """Takipten çıkıldığında bildirim oluştur"""
    Notification.objects.create(
        user=instance.following_user,
        type='follow',
        title='Takipten Çıkılma',
        message=f'{instance.user.username} sizi takip etmeyi bıraktı.',
        related_object_id=instance.user.id,
        related_object_type='user'
    )

@receiver(post_save, sender=UserBlock)
def handle_user_block(sender, instance, created, **kwargs):
    """Kullanıcı engellendiğinde takip ilişkilerini sil"""
    if created:
        # Engellenen kullanıcının takip ilişkilerini sil
        UserFollowing.objects.filter(
            user=instance.user,
            following_user=instance.blocked_user
        ).delete()
        UserFollowing.objects.filter(
            user=instance.blocked_user,
            following_user=instance.user
        ).delete()

@receiver(post_save, sender=UserAchievement)
def create_achievement_notification(sender, instance, created, **kwargs):
    """Başarı kazanıldığında bildirim oluştur"""
    if created:
        Notification.objects.create(
            user=instance.user,
            type='achievement',
            title='Yeni Başarı',
            message=f'"{instance.achievement.name}" başarısını kazandınız!',
            related_object_id=instance.achievement.id,
            related_object_type='achievement'
        ) 