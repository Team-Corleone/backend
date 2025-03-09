from rest_framework import serializers
from .models import (
    Community, CommunityMember, CommunityPost, CommunityComment,
    CommunityBadge, UserBadge, Message, Notification
)
from apps.accounts.serializers import UserPublicProfileSerializer
from apps.movies.serializers import MovieSerializer

class CommunitySerializer(serializers.ModelSerializer):
    """Topluluk serializerı"""
    creator = UserPublicProfileSerializer(read_only=True)
    members_count = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    related_movies = MovieSerializer(many=True, read_only=True)

    class Meta:
        model = Community
        fields = (
            'id', 'name', 'slug', 'description', 'avatar',
            'banner', 'created_at', 'creator', 'rules',
            'is_private', 'members_count', 'is_member',
            'user_role', 'related_movies'
        )
        read_only_fields = ('created_at', 'slug')

    def get_members_count(self, obj):
        return obj.members.count()

    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.members.filter(user=request.user).exists()
        return False

    def get_user_role(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                member = obj.members.get(user=request.user)
                return member.role
            except CommunityMember.DoesNotExist:
                pass
        return None

class CommunityMemberSerializer(serializers.ModelSerializer):
    """Topluluk üyesi serializerı"""
    user = UserPublicProfileSerializer(read_only=True)

    class Meta:
        model = CommunityMember
        fields = (
            'id', 'user', 'role', 'joined_at',
            'is_banned', 'ban_reason', 'custom_title'
        )
        read_only_fields = ('joined_at',)

class CommunityPostSerializer(serializers.ModelSerializer):
    """Topluluk gönderisi serializerı"""
    author = UserPublicProfileSerializer(read_only=True)
    community = CommunitySerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    related_movie = MovieSerializer(read_only=True)
    related_movie_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = CommunityPost
        fields = (
            'id', 'community', 'author', 'title', 'content',
            'created_at', 'updated_at', 'likes_count',
            'comments_count', 'is_liked', 'is_pinned',
            'is_locked', 'related_movie', 'related_movie_id'
        )
        read_only_fields = ('created_at', 'updated_at')

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

class CommunityCommentSerializer(serializers.ModelSerializer):
    """Topluluk yorumu serializerı"""
    author = UserPublicProfileSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = CommunityComment
        fields = (
            'id', 'post', 'author', 'content', 'created_at',
            'updated_at', 'likes_count', 'is_liked',
            'parent', 'replies'
        )
        read_only_fields = ('created_at', 'updated_at')

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

    def get_replies(self, obj):
        if not obj.parent:  # Sadece ana yorumlar için yanıtları getir
            return CommunityCommentSerializer(
                obj.replies.all(),
                many=True,
                context=self.context
            ).data
        return []

class CommunityBadgeSerializer(serializers.ModelSerializer):
    """Topluluk rozeti serializerı"""
    community = CommunitySerializer(read_only=True)

    class Meta:
        model = CommunityBadge
        fields = (
            'id', 'community', 'name', 'description',
            'icon', 'is_special', 'required_points'
        )

class UserBadgeSerializer(serializers.ModelSerializer):
    """Kullanıcı rozeti serializerı"""
    user = UserPublicProfileSerializer(read_only=True)
    badge = CommunityBadgeSerializer(read_only=True)

    class Meta:
        model = UserBadge
        fields = ('id', 'user', 'badge', 'earned_at')
        read_only_fields = ('earned_at',)

class MessageSerializer(serializers.ModelSerializer):
    """Mesaj serializerı"""
    sender = UserPublicProfileSerializer(read_only=True)
    receiver = UserPublicProfileSerializer(read_only=True)
    receiver_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Message
        fields = (
            'id', 'sender', 'receiver', 'receiver_id',
            'content', 'created_at', 'is_read', 'read_at'
        )
        read_only_fields = ('created_at', 'is_read', 'read_at')

class NotificationSerializer(serializers.ModelSerializer):
    """Bildirim serializerı"""
    class Meta:
        model = Notification
        fields = (
            'id', 'type', 'title', 'message', 'created_at',
            'is_read', 'read_at', 'related_object_id',
            'related_object_type'
        )
        read_only_fields = ('created_at', 'is_read', 'read_at') 