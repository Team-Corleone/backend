from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    # Topluluk işlemleri
    path('communities/', views.CommunityListView.as_view(), name='community_list'),
    path('communities/create/', views.CommunityCreateView.as_view(), name='create_community'),
    path('communities/<slug:slug>/', views.CommunityDetailView.as_view(), name='community_detail'),
    path('communities/<slug:slug>/update/', views.CommunityUpdateView.as_view(), name='update_community'),
    path('communities/<slug:slug>/delete/', views.CommunityDeleteView.as_view(), name='delete_community'),
    path('communities/search/', views.CommunitySearchView.as_view(), name='search_communities'),
    
    # Topluluk üyelik işlemleri
    path('communities/<slug:slug>/join/', views.JoinCommunityView.as_view(), name='join_community'),
    path('communities/<slug:slug>/leave/', views.LeaveCommunityView.as_view(), name='leave_community'),
    path('communities/<slug:slug>/members/', views.CommunityMembersView.as_view(), name='community_members'),
    path('communities/<slug:slug>/moderators/', views.CommunityModeratorsView.as_view(), name='community_moderators'),
    
    # Topluluk gönderi işlemleri
    path('communities/<slug:slug>/posts/', views.CommunityPostListView.as_view(), name='community_posts'),
    path('communities/<slug:slug>/posts/create/', views.CommunityPostCreateView.as_view(), name='create_post'),
    path('posts/<int:pk>/', views.CommunityPostDetailView.as_view(), name='post_detail'),
    path('posts/<int:pk>/update/', views.CommunityPostUpdateView.as_view(), name='update_post'),
    path('posts/<int:pk>/delete/', views.CommunityPostDeleteView.as_view(), name='delete_post'),
    path('posts/<int:pk>/like/', views.CommunityPostLikeView.as_view(), name='like_post'),
    path('posts/<int:pk>/pin/', views.CommunityPostPinView.as_view(), name='pin_post'),
    path('posts/<int:pk>/lock/', views.CommunityPostLockView.as_view(), name='lock_post'),
    
    # Yorum işlemleri
    path('posts/<int:post_pk>/comments/', views.CommentListView.as_view(), name='comment_list'),
    path('posts/<int:post_pk>/comments/create/', views.CommentCreateView.as_view(), name='create_comment'),
    path('comments/<int:pk>/', views.CommentDetailView.as_view(), name='comment_detail'),
    path('comments/<int:pk>/update/', views.CommentUpdateView.as_view(), name='update_comment'),
    path('comments/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='delete_comment'),
    path('comments/<int:pk>/like/', views.CommentLikeView.as_view(), name='like_comment'),
    
    # Rozet işlemleri
    path('communities/<slug:slug>/badges/', views.CommunityBadgeListView.as_view(), name='community_badges'),
    path('communities/<slug:slug>/badges/create/', views.CommunityBadgeCreateView.as_view(), name='create_badge'),
    path('badges/<int:pk>/', views.CommunityBadgeDetailView.as_view(), name='badge_detail'),
    path('badges/<int:pk>/update/', views.CommunityBadgeUpdateView.as_view(), name='update_badge'),
    path('badges/<int:pk>/delete/', views.CommunityBadgeDeleteView.as_view(), name='delete_badge'),
    path('badges/<int:pk>/award/', views.AwardBadgeView.as_view(), name='award_badge'),
    
    # Mesajlaşma
    path('messages/', views.MessageListView.as_view(), name='message_list'),
    path('messages/sent/', views.SentMessageListView.as_view(), name='sent_messages'),
    path('messages/create/', views.MessageCreateView.as_view(), name='create_message'),
    path('messages/<int:pk>/', views.MessageDetailView.as_view(), name='message_detail'),
    path('messages/<int:pk>/delete/', views.MessageDeleteView.as_view(), name='delete_message'),
    
    # Bildirimler
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/unread/', views.UnreadNotificationListView.as_view(), name='unread_notifications'),
    path('notifications/<int:pk>/mark-read/', views.MarkNotificationReadView.as_view(), name='mark_notification_read'),
    path('notifications/mark-all-read/', views.MarkAllNotificationsReadView.as_view(), name='mark_all_notifications_read'),
] 