from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserDevice, Achievement, UserAchievement, UserFollowing, UserBlock

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Kullanıcı kaydı serializerı"""
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password_confirm')

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Şifreler eşleşmiyor.")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    """Kullanıcı profili serializerı"""
    following_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    achievements_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'bio', 'avatar',
            'birth_date', 'is_premium', 'premium_until',
            'following_count', 'followers_count', 'achievements_count'
        )
        read_only_fields = ('email', 'is_premium', 'premium_until')

    def get_following_count(self, obj):
        return obj.following.count()

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_achievements_count(self, obj):
        return obj.achievements.count()

class UserPublicProfileSerializer(serializers.ModelSerializer):
    """Herkese açık kullanıcı profili serializerı"""
    following_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    achievements_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    is_blocked = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'bio', 'avatar',
            'following_count', 'followers_count', 'achievements_count',
            'is_following', 'is_blocked'
        )

    def get_following_count(self, obj):
        return obj.following.count()

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_achievements_count(self, obj):
        return obj.achievements.count()

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserFollowing.objects.filter(
                user=request.user,
                following_user=obj
            ).exists()
        return False

    def get_is_blocked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserBlock.objects.filter(
                user=request.user,
                blocked_user=obj
            ).exists()
        return False

class UserDeviceSerializer(serializers.ModelSerializer):
    """Kullanıcı cihazı serializerı"""
    class Meta:
        model = UserDevice
        fields = ('id', 'device_id', 'device_type', 'device_name', 'last_login', 'is_active')
        read_only_fields = ('last_login',)

class AchievementSerializer(serializers.ModelSerializer):
    """Başarı serializerı"""
    class Meta:
        model = Achievement
        fields = ('id', 'name', 'description', 'icon', 'points')

class UserAchievementSerializer(serializers.ModelSerializer):
    """Kullanıcı başarısı serializerı"""
    achievement = AchievementSerializer(read_only=True)

    class Meta:
        model = UserAchievement
        fields = ('id', 'achievement', 'earned_at')
        read_only_fields = ('earned_at',)

class UserFollowingSerializer(serializers.ModelSerializer):
    """Kullanıcı takip serializerı"""
    following_user = UserPublicProfileSerializer(read_only=True)

    class Meta:
        model = UserFollowing
        fields = ('id', 'following_user', 'created_at')
        read_only_fields = ('created_at',)

class UserBlockSerializer(serializers.ModelSerializer):
    """Kullanıcı engelleme serializerı"""
    blocked_user = UserPublicProfileSerializer(read_only=True)

    class Meta:
        model = UserBlock
        fields = ('id', 'blocked_user', 'reason', 'created_at')
        read_only_fields = ('created_at',) 