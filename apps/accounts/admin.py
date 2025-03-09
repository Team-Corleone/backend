from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserDevice, UserFollowing, UserBlock, Achievement, UserAchievement

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_premium')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_premium')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('Premium Bilgileri', {'fields': ('is_premium', 'premium_until')}),
        ('Ek Bilgiler', {'fields': ('bio', 'avatar', 'birth_date')}),
    )

@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_name', 'device_type', 'last_login', 'is_active')
    list_filter = ('device_type', 'is_active')
    search_fields = ('user__username', 'device_name')

@admin.register(UserFollowing)
class UserFollowingAdmin(admin.ModelAdmin):
    list_display = ('user', 'following_user', 'created_at')
    search_fields = ('user__username', 'following_user__username')

@admin.register(UserBlock)
class UserBlockAdmin(admin.ModelAdmin):
    list_display = ('user', 'blocked_user', 'created_at')
    search_fields = ('user__username', 'blocked_user__username')

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'points')
    search_fields = ('name',)

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'earned_at')
    list_filter = ('achievement',)
    search_fields = ('user__username', 'achievement__name') 