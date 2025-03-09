from rest_framework import generics, status, views, filters
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import (
    Community, CommunityMember, CommunityPost, CommunityComment,
    CommunityBadge, UserBadge, Message, Notification
)
from .serializers import (
    CommunitySerializer, CommunityMemberSerializer, CommunityPostSerializer,
    CommunityCommentSerializer, CommunityBadgeSerializer, UserBadgeSerializer,
    MessageSerializer, NotificationSerializer
)
from .permissions import (
    IsCommunityAdmin, IsCommunityModerator, IsCommunityMember,
    IsPostAuthorOrReadOnly, IsCommentAuthorOrReadOnly
)
from django.db.models import Q

class CommunityListView(generics.ListAPIView):
    """Topluluk listesi"""
    queryset = Community.objects.filter(is_private=False)
    serializer_class = CommunitySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class CommunityCreateView(generics.CreateAPIView):
    """Topluluk oluşturma"""
    serializer_class = CommunitySerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        community = serializer.save(creator=self.request.user)
        CommunityMember.objects.create(
            community=community,
            user=self.request.user,
            role='admin'
        )






class CommunityListView(generics.ListAPIView):
    """Topluluk listesi"""
    queryset = Community.objects.filter(is_private=False)
    serializer_class = CommunitySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']



class MessageListView(generics.ListCreateAPIView):
    """Mesaj listesi ve gönderme"""
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Message.objects.filter(receiver=self.request.user)
    
class MessageDetailView(generics.RetrieveDestroyAPIView):
    """Mesaj detay ve silme"""
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Message.objects.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user)
        )
    
class MessageCreateView(generics.CreateAPIView):
    """Mesaj oluşturma"""
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class MessageDeleteView(generics.DestroyAPIView):
    """Mesaj silme"""
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Message.objects.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user)
        )
    
class SentMessageListView(generics.ListAPIView):
    """Gönderilen mesajlar"""
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user)
    
class NotificationListView(generics.ListAPIView):
    """Bildirim listesi"""
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

class CommunityDetailView(generics.RetrieveAPIView):
    """Topluluk detayı"""
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    lookup_field = 'slug'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Community.objects.all()
        return Community.objects.filter(is_private=False)

class CommunityUpdateView(generics.UpdateAPIView):
    """Topluluk güncelleme"""
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = (IsAuthenticated, IsCommunityAdmin)
    lookup_field = 'slug'

class CommunityDeleteView(generics.DestroyAPIView):
    """Topluluk silme"""
    queryset = Community.objects.all()
    permission_classes = (IsAuthenticated, IsCommunityAdmin)
    lookup_field = 'slug'

class JoinCommunityView(views.APIView):
    """Topluluğa katılma"""
    permission_classes = (IsAuthenticated,)

    def post(self, request, slug):
        community = get_object_or_404(Community, slug=slug)
        if community.is_private:
            return Response(
                {'detail': 'Bu topluluk özel.'},
                status=status.HTTP_403_FORBIDDEN
            )
        member, created = CommunityMember.objects.get_or_create(
            community=community,
            user=request.user,
            defaults={'role': 'member'}
        )
        if not created:
            return Response(
                {'detail': 'Zaten üyesiniz.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response({'detail': 'Topluluğa katıldınız.'})

class LeaveCommunityView(views.APIView):
    """Topluluktan ayrılma"""
    permission_classes = (IsAuthenticated,)

    def post(self, request, slug):
        community = get_object_or_404(Community, slug=slug)
        try:
            member = CommunityMember.objects.get(
                community=community,
                user=request.user
            )
            if member.role == 'admin' and community.members.filter(role='admin').count() == 1:
                return Response(
                    {'detail': 'Son yönetici olduğunuz için ayrılamazsınız.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            member.delete()
            return Response({'detail': 'Topluluktan ayrıldınız.'})
        except CommunityMember.DoesNotExist:
            return Response(
                {'detail': 'Üye değilsiniz.'},
                status=status.HTTP_400_BAD_REQUEST
            )

class CommunityMembersView(generics.ListAPIView):
    """Topluluk üyeleri"""
    serializer_class = CommunityMemberSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return CommunityMember.objects.filter(
            community__slug=self.kwargs['slug']
        )

class CommunityModeratorsView(generics.ListAPIView):
    """Topluluk moderatörleri"""
    serializer_class = CommunityMemberSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return CommunityMember.objects.filter(
            community__slug=self.kwargs['slug'],
            role__in=['admin', 'moderator']
        )

class CommunityPostListView(generics.ListCreateAPIView):
    """Topluluk gönderileri"""
    serializer_class = CommunityPostSerializer
    permission_classes = (IsAuthenticated, IsCommunityMember)

    def get_queryset(self):
        return CommunityPost.objects.filter(
            community__slug=self.kwargs['slug']
        ).order_by('-is_pinned', '-created_at')

    def perform_create(self, serializer):
        community = get_object_or_404(Community, slug=self.kwargs['slug'])
        serializer.save(community=community, author=self.request.user)

class CommunityPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Gönderi detay, güncelleme ve silme"""
    queryset = CommunityPost.objects.all()
    serializer_class = CommunityPostSerializer
    permission_classes = (IsAuthenticated, IsPostAuthorOrReadOnly)

class CommunityPostLikeView(views.APIView):
    """Gönderi beğenme"""
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        post = get_object_or_404(CommunityPost, pk=pk)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            return Response({'detail': 'Beğeni kaldırıldı.'})
        post.likes.add(request.user)
        return Response({'detail': 'Gönderi beğenildi.'})

class CommunityPostPinView(views.APIView):
    """Gönderi sabitleme"""
    permission_classes = (IsAuthenticated, IsCommunityModerator)

    def post(self, request, pk):
        post = get_object_or_404(CommunityPost, pk=pk)
        post.is_pinned = not post.is_pinned
        post.save()
        return Response({
            'detail': 'Gönderi sabitlendi.' if post.is_pinned else 'Gönderi sabitlemesi kaldırıldı.'
        })

class CommunityPostLockView(views.APIView):
    """Gönderi kilitleme"""
    permission_classes = (IsAuthenticated, IsCommunityModerator)

    def post(self, request, pk):
        post = get_object_or_404(CommunityPost, pk=pk)
        post.is_locked = not post.is_locked
        post.save()
        return Response({
            'detail': 'Gönderi kilitlendi.' if post.is_locked else 'Gönderi kilidi kaldırıldı.'
        })

class CommunityPostCreateView(generics.CreateAPIView):
    """Topluluk gönderisi oluşturma"""
    serializer_class = CommunityPostSerializer
    permission_classes = (IsAuthenticated, IsCommunityMember)

    def perform_create(self, serializer):
        community = get_object_or_404(Community, slug=self.kwargs['slug'])
        serializer.save(community=community, author=self.request.user)

class CommunityPostUpdateView(generics.UpdateAPIView):
    """Topluluk gönderisi güncelleme"""
    queryset = CommunityPost.objects.all()
    serializer_class = CommunityPostSerializer
    permission_classes = (IsAuthenticated, IsPostAuthorOrReadOnly)

class CommunityPostDeleteView(generics.DestroyAPIView):
    """Topluluk gönderisi silme"""
    queryset = CommunityPost.objects.all()
    permission_classes = (IsAuthenticated, IsPostAuthorOrReadOnly)

class CommentListView(generics.ListCreateAPIView):
    """Yorum listesi ve oluşturma"""
    serializer_class = CommunityCommentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return CommunityComment.objects.filter(
            post_id=self.kwargs['post_pk']
        ).order_by('created_at')

    def perform_create(self, serializer):
        post = get_object_or_404(CommunityPost, pk=self.kwargs['post_pk'])
        if post.is_locked:
            return Response(
                {'detail': 'Bu gönderi kilitli.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save(post=post, author=self.request.user)

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Yorum detay, güncelleme ve silme"""
    queryset = CommunityComment.objects.all()
    serializer_class = CommunityCommentSerializer
    permission_classes = (IsAuthenticated, IsCommentAuthorOrReadOnly)

class CommentLikeView(views.APIView):
    """Yorum beğenme"""
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        comment = get_object_or_404(CommunityComment, pk=pk)
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)
            return Response({'detail': 'Beğeni kaldırıldı.'})
        comment.likes.add(request.user)
        return Response({'detail': 'Yorum beğenildi.'})

class CommunityBadgeListView(generics.ListCreateAPIView):
    """Topluluk rozetleri"""
    serializer_class = CommunityBadgeSerializer
    permission_classes = (IsAuthenticated, IsCommunityModerator)

    def get_queryset(self):
        return CommunityBadge.objects.filter(
            community__slug=self.kwargs['slug']
        )

    def perform_create(self, serializer):
        community = get_object_or_404(Community, slug=self.kwargs['slug'])
        serializer.save(community=community)

class CommunityBadgeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Rozet detay, güncelleme ve silme"""
    queryset = CommunityBadge.objects.all()
    serializer_class = CommunityBadgeSerializer
    permission_classes = (IsAuthenticated, IsCommunityModerator)

class CommunityBadgeCreateView(generics.CreateAPIView):
    """Topluluk rozeti oluşturma"""
    serializer_class = CommunityBadgeSerializer
    permission_classes = (IsAuthenticated, IsCommunityModerator)

    def perform_create(self, serializer):
        community = get_object_or_404(Community, slug=self.kwargs['slug'])
        serializer.save(community=community)

class CommunityBadgeUpdateView(generics.UpdateAPIView):
    """Topluluk rozeti güncelleme"""
    queryset = CommunityBadge.objects.all()
    serializer_class = CommunityBadgeSerializer
    permission_classes = (IsAuthenticated, IsCommunityModerator)

class CommunityBadgeDeleteView(generics.DestroyAPIView):
    """Topluluk rozeti silme"""
    queryset = CommunityBadge.objects.all()
    permission_classes = (IsAuthenticated, IsCommunityModerator)

class AwardBadgeView(views.APIView):
    """Rozet verme"""
    permission_classes = (IsAuthenticated, IsCommunityModerator)

    def post(self, request, pk):
        badge = get_object_or_404(CommunityBadge, pk=pk)
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'detail': 'Kullanıcı ID gerekli.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            member = CommunityMember.objects.get(
                community=badge.community,
                user_id=user_id
            )
            UserBadge.objects.create(
                user=member.user,
                badge=badge
            )
            return Response({'detail': 'Rozet verildi.'})
        except CommunityMember.DoesNotExist:
            return Response(
                {'detail': 'Kullanıcı bu topluluğun üyesi değil.'},
                status=status.HTTP_400_BAD_REQUEST
            )

class MessageListView(generics.ListCreateAPIView):
    """Mesaj listesi ve gönderme"""
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Message.objects.filter(receiver=self.request.user)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class SentMessageListView(generics.ListAPIView):
    """Gönderilen mesajlar"""
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user)

class MessageDetailView(generics.RetrieveDestroyAPIView):
    """Mesaj detay ve silme"""
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Message.objects.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user)
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.receiver == request.user and not instance.is_read:
            instance.is_read = True
            instance.read_at = timezone.now()
            instance.save()
        return super().retrieve(request, *args, **kwargs)

class NotificationListView(generics.ListAPIView):
    """Bildirim listesi"""
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

class UnreadNotificationListView(generics.ListAPIView):
    """Okunmamış bildirimler"""
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user,
            is_read=False
        )

class MarkNotificationReadView(views.APIView):
    """Bildirimi okundu olarak işaretleme"""
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        notification = get_object_or_404(
            Notification,
            pk=pk,
            user=request.user
        )
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response({'detail': 'Bildirim okundu olarak işaretlendi.'})

class MarkAllNotificationsReadView(views.APIView):
    """Tüm bildirimleri okundu olarak işaretleme"""
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        return Response({'detail': 'Tüm bildirimler okundu olarak işaretlendi.'})

class CommunitySearchView(generics.ListAPIView):
    """Topluluk arama"""
    serializer_class = CommunitySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Community.objects.all()
        return Community.objects.filter(is_private=False)

class CommentCreateView(generics.CreateAPIView):
    """Yorum oluşturma"""
    serializer_class = CommunityCommentSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        post = get_object_or_404(CommunityPost, pk=self.kwargs['post_pk'])
        if post.is_locked:
            return Response(
                {'detail': 'Bu gönderi kilitli.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save(post=post, author=self.request.user)

class CommentUpdateView(generics.UpdateAPIView):
    """Yorum güncelleme"""
    queryset = CommunityComment.objects.all()
    serializer_class = CommunityCommentSerializer
    permission_classes = (IsAuthenticated, IsCommentAuthorOrReadOnly)

class CommentDeleteView(generics.DestroyAPIView):
    """Yorum silme"""
    queryset = CommunityComment.objects.all()
    permission_classes = (IsAuthenticated, IsCommentAuthorOrReadOnly)

class MessageCreateView(generics.CreateAPIView):
    """Mesaj oluşturma"""
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class MessageDeleteView(generics.DestroyAPIView):
    """Mesaj silme"""
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Message.objects.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user)
        ) 