from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User
from apps.movies.models import Movie

class Community(models.Model):
    """Film/dizi topluluğu"""
    name = models.CharField(_('Topluluk Adı'), max_length=255)
    slug = models.SlugField(_('URL'), unique=True)
    description = models.TextField(_('Açıklama'))
    avatar = models.ImageField(_('Avatar'), upload_to='communities/avatars/', null=True, blank=True)
    banner = models.ImageField(_('Banner'), upload_to='communities/banners/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_communities')
    members = models.ManyToManyField(User, through='CommunityMember', related_name='joined_communities')
    rules = models.TextField(_('Kurallar'), blank=True)
    is_private = models.BooleanField(_('Özel'), default=False)
    related_movies = models.ManyToManyField(Movie, related_name='communities', blank=True)
    
    class Meta:
        verbose_name = _('Topluluk')
        verbose_name_plural = _('Topluluklar')

class CommunityMember(models.Model):
    """Topluluk üyesi"""
    ROLE_CHOICES = [
        ('admin', _('Yönetici')),
        ('moderator', _('Moderatör')),
        ('member', _('Üye')),
    ]
    
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(_('Rol'), max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_banned = models.BooleanField(_('Engellenmiş'), default=False)
    ban_reason = models.TextField(_('Engelleme Nedeni'), blank=True)
    custom_title = models.CharField(_('Özel Başlık'), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _('Topluluk Üyesi')
        verbose_name_plural = _('Topluluk Üyeleri')
        unique_together = ('community', 'user')

class CommunityPost(models.Model):
    """Topluluk gönderisi"""
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_posts')
    title = models.CharField(_('Başlık'), max_length=255)
    content = models.TextField(_('İçerik'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_community_posts')
    is_pinned = models.BooleanField(_('Sabitlenmiş'), default=False)
    is_locked = models.BooleanField(_('Kilitli'), default=False)
    related_movie = models.ForeignKey(Movie, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = _('Gönderi')
        verbose_name_plural = _('Gönderiler')
        ordering = ['-created_at']

class CommunityComment(models.Model):
    """Topluluk gönderisi yorumu"""
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_comments')
    content = models.TextField(_('İçerik'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_community_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    class Meta:
        verbose_name = _('Yorum')
        verbose_name_plural = _('Yorumlar')
        ordering = ['created_at']

class CommunityBadge(models.Model):
    """Topluluk rozetleri"""
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='badges')
    name = models.CharField(_('Rozet Adı'), max_length=100)
    description = models.TextField(_('Açıklama'))
    icon = models.ImageField(_('İkon'), upload_to='communities/badges/')
    is_special = models.BooleanField(_('Özel Rozet'), default=False)
    required_points = models.IntegerField(_('Gerekli Puan'), default=0)
    
    class Meta:
        verbose_name = _('Rozet')
        verbose_name_plural = _('Rozetler')

class UserBadge(models.Model):
    """Kullanıcı rozetleri"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_badges')
    badge = models.ForeignKey(CommunityBadge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Kullanıcı Rozeti')
        verbose_name_plural = _('Kullanıcı Rozetleri')
        unique_together = ('user', 'badge')

class Message(models.Model):
    """Özel mesajlar"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(_('Mesaj'))
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(_('Okundu'), default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('Mesaj')
        verbose_name_plural = _('Mesajlar')
        ordering = ['created_at']

class Notification(models.Model):
    """Bildirimler"""
    NOTIFICATION_TYPES = [
        ('follow', _('Takip')),
        ('like', _('Beğeni')),
        ('comment', _('Yorum')),
        ('mention', _('Bahsetme')),
        ('badge', _('Rozet')),
        ('achievement', _('Başarı')),
        ('community', _('Topluluk')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(_('Bildirim Tipi'), max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(_('Başlık'), max_length=255)
    message = models.TextField(_('Mesaj'))
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(_('Okundu'), default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    related_object_id = models.IntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = _('Bildirim')
        verbose_name_plural = _('Bildirimler')
        ordering = ['-created_at'] 