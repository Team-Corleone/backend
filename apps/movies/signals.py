from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import UserMovieRating, UserMovieList
from apps.social.models import Notification

@receiver(post_save, sender=UserMovieRating)
def create_rating_notification(sender, instance, created, **kwargs):
    """Film değerlendirmesi yapıldığında bildirim oluştur"""
    if created:
        # Film değerlendirmesi yapan kullanıcının takipçilerine bildir
        for follower in instance.user.followers.all():
            Notification.objects.create(
                user=follower.user,
                type='like',
                title='Yeni Film Değerlendirmesi',
                message=f'{instance.user.username} "{instance.movie.title}" filmini değerlendirdi.',
                related_object_id=instance.id,
                related_object_type='movie_rating'
            )

@receiver(m2m_changed, sender=UserMovieRating.likes.through)
def create_rating_like_notification(sender, instance, action, pk_set, **kwargs):
    """Film değerlendirmesi beğenildiğinde bildirim oluştur"""
    if action == "post_add":
        for user_id in pk_set:
            Notification.objects.create(
                user=instance.user,
                type='like',
                title='Değerlendirme Beğenisi',
                message=f'{user_id} "{instance.movie.title}" filmi için yaptığınız değerlendirmeyi beğendi.',
                related_object_id=instance.id,
                related_object_type='movie_rating'
            )

@receiver(post_save, sender=UserMovieList)
def create_list_notification(sender, instance, created, **kwargs):
    """Film listesi oluşturulduğunda bildirim oluştur"""
    if created and instance.is_public:
        # Liste oluşturan kullanıcının takipçilerine bildir
        for follower in instance.user.followers.all():
            Notification.objects.create(
                user=follower.user,
                type='list',
                title='Yeni Film Listesi',
                message=f'{instance.user.username} yeni bir film listesi oluşturdu: {instance.name}',
                related_object_id=instance.id,
                related_object_type='movie_list'
            ) 