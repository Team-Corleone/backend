from rest_framework import permissions

class IsCommunityAdmin(permissions.BasePermission):
    """
    Topluluk yöneticisine erişim izni verir.
    """

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(user=request.user, role='admin').exists()

class IsCommunityModerator(permissions.BasePermission):
    """
    Topluluk moderatörüne erişim izni verir.
    """

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(
            user=request.user,
            role__in=['admin', 'moderator']
        ).exists()

class IsCommunityMember(permissions.BasePermission):
    """
    Topluluk üyesine erişim izni verir.
    """

    def has_permission(self, request, view):
        community_slug = view.kwargs.get('slug')
        if not community_slug:
            return False
        return request.user.joined_communities.filter(slug=community_slug).exists()

class IsPostAuthorOrReadOnly(permissions.BasePermission):
    """
    Gönderi sahibine düzenleme izni verir.
    Diğer kullanıcılar sadece görüntüleyebilir.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or obj.community.members.filter(
            user=request.user,
            role__in=['admin', 'moderator']
        ).exists()

class IsCommentAuthorOrReadOnly(permissions.BasePermission):
    """
    Yorum sahibine düzenleme izni verir.
    Diğer kullanıcılar sadece görüntüleyebilir.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or obj.post.community.members.filter(
            user=request.user,
            role__in=['admin', 'moderator']
        ).exists()

class IsMessageParticipant(permissions.BasePermission):
    """
    Mesaj katılımcılarına erişim izni verir.
    """

    def has_object_permission(self, request, view, obj):
        return request.user in [obj.sender, obj.receiver] 