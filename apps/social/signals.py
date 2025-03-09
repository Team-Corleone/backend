from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Community, CommunityMember, CommunityPost, CommunityComment, CommunityBadge, UserBadge, Message, Notification

@receiver(post_save, sender=CommunityMember)
def create_member_notification(sender, instance, created, **kwargs):
    """Topluluğa yeni üye katıldığında bildirim oluştur"""
    if created:
        # Topluluk yöneticilerine bildir
        admin_members = instance.community.members.filter(role='admin')
        for admin in admin_members:
            Notification.objects.create(
                user=admin.user,
                type='community',
                title='Yeni Üye',
                message=f'{instance.user.username} topluluğa katıldı.',
                related_object_id=instance.id,
                related_object_type='community_member'
            )

@receiver(post_save, sender=CommunityPost)
def create_post_notification(sender, instance, created, **kwargs):
    """Toplulukta yeni gönderi oluşturulduğunda bildirim oluştur"""
    if created:
        # Topluluk üyelerine bildir
        for member in instance.community.members.all():
            if member.user != instance.author:
                Notification.objects.create(
                    user=member.user,
                    type='community',
                    title='Yeni Gönderi',
                    message=f'{instance.author.username} "{instance.community.name}" topluluğunda yeni bir gönderi paylaştı.',
                    related_object_id=instance.id,
                    related_object_type='community_post'
                )

@receiver(post_save, sender=CommunityComment)
def create_comment_notification(sender, instance, created, **kwargs):
    """Gönderiye yorum yapıldığında bildirim oluştur"""
    if created:
        # Gönderi sahibine bildir
        if instance.author != instance.post.author:
            Notification.objects.create(
                user=instance.post.author,
                type='community',
                title='Yeni Yorum',
                message=f'{instance.author.username} gönderinize yorum yaptı.',
                related_object_id=instance.id,
                related_object_type='community_comment'
            )
        
        # Üst yorumun sahibine bildir
        if instance.parent and instance.parent.author != instance.author:
            Notification.objects.create(
                user=instance.parent.author,
                type='community',
                title='Yorum Yanıtı',
                message=f'{instance.author.username} yorumunuza yanıt verdi.',
                related_object_id=instance.id,
                related_object_type='community_comment'
            )

@receiver(post_save, sender=UserBadge)
def create_badge_notification(sender, instance, created, **kwargs):
    """Kullanıcı rozet kazandığında bildirim oluştur"""
    if created:
        Notification.objects.create(
            user=instance.user,
            type='badge',
            title='Yeni Rozet',
            message=f'"{instance.badge.community.name}" topluluğunda yeni bir rozet kazandınız: {instance.badge.name}',
            related_object_id=instance.id,
            related_object_type='user_badge'
        )

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """Yeni mesaj gönderildiğinde bildirim oluştur"""
    if created:
        Notification.objects.create(
            user=instance.receiver,
            type='message',
            title='Yeni Mesaj',
            message=f'{instance.sender.username} size yeni bir mesaj gönderdi.',
            related_object_id=instance.id,
            related_object_type='message'
        ) 