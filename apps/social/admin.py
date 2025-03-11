from django.contrib import admin
from .models import (
    Community, CommunityMember, CommunityPost, CommunityComment,
    CommunityBadge, UserBadge, Message, Notification
)

@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'created_at', 'is_private')
    list_filter = ('is_private',)
    search_fields = ('name', 'description')
    filter_horizontal = ()  # ✅ Remove problematic fields

    prepopulated_fields = {'slug': ('name',)}

@admin.register(CommunityMember)
class CommunityMemberAdmin(admin.ModelAdmin):
    list_display = ('community', 'user', 'role', 'joined_at', 'is_banned')
    list_filter = ('role', 'is_banned')
    search_fields = ('community__name', 'user__username')

@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'community', 'author', 'created_at', 'is_pinned', 'is_locked')
    list_filter = ('is_pinned', 'is_locked', 'community')
    search_fields = ('title', 'content', 'author__username')
    filter_horizontal = ('likes',)

@admin.register(CommunityComment)
class CommunityCommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')
    search_fields = ('content', 'author__username', 'post__title')
    filter_horizontal = ('likes',)

@admin.register(CommunityBadge)
class CommunityBadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'community', 'is_special', 'required_points')
    list_filter = ('is_special', 'community')
    search_fields = ('name', 'description')

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'earned_at')
    search_fields = ('user__username', 'badge__name')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'created_at', 'is_read')
    list_filter = ('is_read',)
    search_fields = ('sender__username', 'receiver__username', 'content')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'title', 'created_at', 'is_read')
    list_filter = ('type', 'is_read')
    search_fields = ('user__username', 'title', 'message') 