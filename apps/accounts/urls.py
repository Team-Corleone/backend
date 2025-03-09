from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Kimlik doğrulama
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('verify-email/<str:token>/', views.EmailVerificationView.as_view(), name='verify_email'),
    path('password/reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password/reset/confirm/<str:token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # Kullanıcı profili
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='profile_update'),
    path('profile/password/', views.PasswordChangeView.as_view(), name='password_change'),
    path('profile/<str:username>/', views.UserPublicProfileView.as_view(), name='public_profile'),
    
    # Takip sistemi
    path('follow/<str:username>/', views.UserFollowView.as_view(), name='follow'),
    path('unfollow/<str:username>/', views.UserUnfollowView.as_view(), name='unfollow'),
    path('followers/', views.UserFollowersView.as_view(), name='followers'),
    path('following/', views.UserFollowingView.as_view(), name='following'),
    
    # Engelleme sistemi
    path('block/<str:username>/', views.UserBlockView.as_view(), name='block'),
    path('unblock/<str:username>/', views.UserUnblockView.as_view(), name='unblock'),
    path('blocked-users/', views.BlockedUsersView.as_view(), name='blocked_users'),
    
    # Cihaz yönetimi
    path('devices/', views.UserDevicesView.as_view(), name='devices'),
    path('devices/<int:pk>/', views.UserDeviceDetailView.as_view(), name='device_detail'),
    
    # Başarılar
    path('achievements/', views.UserAchievementsView.as_view(), name='achievements'),
    path('achievements/<int:pk>/', views.AchievementDetailView.as_view(), name='achievement_detail'),
    
    # Premium üyelik
    path('premium/subscribe/', views.PremiumSubscriptionView.as_view(), name='premium_subscribe'),
    path('premium/cancel/', views.PremiumCancellationView.as_view(), name='premium_cancel'),
    path('premium/status/', views.PremiumStatusView.as_view(), name='premium_status'),
] 