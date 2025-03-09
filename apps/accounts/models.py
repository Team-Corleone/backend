from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Özelleştirilmiş kullanıcı modeli"""
    bio = models.TextField(_('Biyografi'), blank=True)
    avatar = models.ImageField(_('Profil Fotoğrafı'), upload_to='avatars/', null=True, blank=True)
    birth_date = models.DateField(_('Doğum Tarihi'), null=True, blank=True)
    is_premium = models.BooleanField(_('Premium Üye'), default=False)
    premium_until = models.DateTimeField(_('Premium Üyelik Bitiş'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Kullanıcı')
        verbose_name_plural = _('Kullanıcılar')

class UserDevice(models.Model):
    """Kullanıcı cihaz bilgileri"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    device_id = models.CharField(_('Cihaz ID'), max_length=255)
    device_type = models.CharField(_('Cihaz Tipi'), max_length=50)
    device_name = models.CharField(_('Cihaz Adı'), max_length=255)
    last_login = models.DateTimeField(_('Son Giriş'), auto_now=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    
    class Meta:
        verbose_name = _('Kullanıcı Cihazı')
        verbose_name_plural = _('Kullanıcı Cihazları')
        unique_together = ('user', 'device_id')

class UserFollowing(models.Model):
    """Kullanıcı takip sistemi"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Takip')
        verbose_name_plural = _('Takipler')
        unique_together = ('user', 'following_user')

class UserBlock(models.Model):
    """Kullanıcı engelleme sistemi"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocking')
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by')
    created_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(_('Engelleme Nedeni'), blank=True)
    
    class Meta:
        verbose_name = _('Engelleme')
        verbose_name_plural = _('Engellemeler')
        unique_together = ('user', 'blocked_user')

class Achievement(models.Model):
    """Başarı/Rozet sistemi"""
    name = models.CharField(_('Başarı Adı'), max_length=100)
    description = models.TextField(_('Açıklama'))
    icon = models.ImageField(_('İkon'), upload_to='achievements/')
    points = models.IntegerField(_('Puan'), default=0)
    
    class Meta:
        verbose_name = _('Başarı')
        verbose_name_plural = _('Başarılar')

class UserAchievement(models.Model):
    """Kullanıcı başarıları"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Kullanıcı Başarısı')
        verbose_name_plural = _('Kullanıcı Başarıları')
        unique_together = ('user', 'achievement') 