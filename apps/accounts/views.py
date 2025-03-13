from rest_framework import generics, status, views
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserPublicProfileSerializer,
    UserDeviceSerializer,
    AchievementSerializer,
    UserFollowingSerializer,
    UserBlockSerializer,
)
from .models import UserDevice, Achievement, UserFollowing, UserBlock
#test google sing in
from django.shortcuts import render,redirect
from django.contrib.auth import logout


def home(request):
    return render(request, 'home.html')
def logout_view(request):
    logout(request)
    return redirect('/')











User = get_user_model()
from django.urls import reverse
def send_verification_email(user, request):
    """Kullanıcıya doğrulama e-postası gönder"""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    verification_url = request.build_absolute_uri(
        reverse("accounts:email-verify", kwargs={"uidb64": uid, "token": token})
    )

    subject = "Hesabınızı Doğrulayın"
    message = f"Merhaba {user.username},\n\nHesabınızı doğrulamak için aşağıdaki linke tıklayın:\n\n{verification_url}"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
class UserRegistrationView(generics.CreateAPIView):
    """Kullanıcı kaydı"""
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(email=response.data["email"])
        send_verification_email(user, request)  # ✅ Kayıt olunca doğrulama maili gönder
        
        return Response(
            {"detail": "Kayıt başarılı! Lütfen e-postanızı doğrulayın."},
            status=status.HTTP_201_CREATED,
        )

class EmailVerificationView(views.APIView):
    """E-posta doğrulama"""
    permission_classes = (AllowAny,)

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if default_token_generator.check_token(user, token):
                user.is_verified = True
                user.save()
                return Response({"detail": "E-posta doğrulandı!"}, status=status.HTTP_200_OK)

            return Response({"detail": "Geçersiz veya süresi dolmuş token!"}, status=status.HTTP_400_BAD_REQUEST)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Geçersiz bağlantı!"}, status=status.HTTP_400_BAD_REQUEST)
class PasswordResetView(views.APIView):
    """Şifre sıfırlama"""
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"{settings.FRONTEND_URL}/password-reset/{uid}/{token}/"
            
            send_mail(
                'Şifre Sıfırlama',
                f'Şifrenizi sıfırlamak için linke tıklayın: {reset_url}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return Response({'detail': 'Şifre sıfırlama linki email adresinize gönderildi.'})
        except User.DoesNotExist:
            return Response(
                {'detail': 'Bu email adresi ile kayıtlı kullanıcı bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )

class PasswordResetConfirmView(views.APIView):
    """Şifre sıfırlama onayı"""
    permission_classes = (AllowAny,)

    def post(self, request, token):
        try:
            uid = force_str(urlsafe_base64_decode(request.data.get('uid')))
            user = User.objects.get(pk=uid)
            
            if default_token_generator.check_token(user, token):
                user.set_password(request.data.get('new_password'))
                user.save()
                return Response({'detail': 'Şifreniz başarıyla değiştirildi.'})
            return Response(
                {'detail': 'Geçersiz token.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {'detail': 'Geçersiz link.'},
                status=status.HTTP_400_BAD_REQUEST
            )

class UserProfileView(generics.RetrieveUpdateAPIView):
    """Kullanıcı profili görüntüleme ve güncelleme"""
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

class UserProfileUpdateView(generics.UpdateAPIView):
    """Kullanıcı profili güncelleme"""
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

class PasswordChangeView(views.APIView):
    """Şifre değiştirme"""
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        if not user.check_password(request.data.get('old_password')):
            return Response(
                {'detail': 'Mevcut şifre yanlış.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(request.data.get('new_password'))
        user.save()
        return Response({'detail': 'Şifreniz başarıyla değiştirildi.'})

class UserPublicProfileView(generics.RetrieveAPIView):
    """Kullanıcı profili görüntüleme (herkese açık)"""
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserPublicProfileSerializer
    lookup_field = 'username'

class UserFollowView(views.APIView):
    """Kullanıcı takip etme"""
    permission_classes = (IsAuthenticated,)

    def post(self, request, username):
        try:
            user_to_follow = User.objects.get(username=username)
            UserFollowing.objects.get_or_create(
                user=request.user,
                following_user=user_to_follow
            )
            return Response({'detail': f'{username} kullanıcısı takip edildi.'})
        except User.DoesNotExist:
            return Response(
                {'detail': 'Kullanıcı bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )

class UserUnfollowView(views.APIView):
    """Kullanıcı takibi bırakma"""
    permission_classes = (IsAuthenticated,)

    def post(self, request, username):
        try:
            user_to_unfollow = User.objects.get(username=username)
            UserFollowing.objects.filter(
                user=request.user,
                following_user=user_to_unfollow
            ).delete()
            return Response({'detail': f'{username} kullanıcısının takibi bırakıldı.'})
        except User.DoesNotExist:
            return Response(
                {'detail': 'Kullanıcı bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )

class UserFollowersView(generics.ListAPIView):
    """Takipçiler listesi"""
    permission_classes = (IsAuthenticated,)
    serializer_class = UserFollowingSerializer

    def get_queryset(self):
        return UserFollowing.objects.filter(following_user=self.request.user)

class UserFollowingView(generics.ListAPIView):
    """Takip edilenler listesi"""
    permission_classes = (IsAuthenticated,)
    serializer_class = UserFollowingSerializer

    def get_queryset(self):
        return UserFollowing.objects.filter(user=self.request.user)

class UserBlockView(views.APIView):
    """Kullanıcı engelleme"""
    permission_classes = (IsAuthenticated,)

    def post(self, request, username):
        try:
            user_to_block = User.objects.get(username=username)
            UserBlock.objects.get_or_create(
                user=request.user,
                blocked_user=user_to_block
            )
            return Response({'detail': f'{username} kullanıcısı engellendi.'})
        except User.DoesNotExist:
            return Response(
                {'detail': 'Kullanıcı bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )

class UserUnblockView(views.APIView):
    """Kullanıcı engelini kaldırma"""
    permission_classes = (IsAuthenticated,)

    def post(self, request, username):
        try:
            user_to_unblock = User.objects.get(username=username)
            UserBlock.objects.filter(
                user=request.user,
                blocked_user=user_to_unblock
            ).delete()
            return Response({'detail': f'{username} kullanıcısının engeli kaldırıldı.'})
        except User.DoesNotExist:
            return Response(
                {'detail': 'Kullanıcı bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )

class BlockedUsersView(generics.ListAPIView):
    """Engellenen kullanıcılar listesi"""
    permission_classes = (IsAuthenticated,)
    serializer_class = UserBlockSerializer

    def get_queryset(self):
        return UserBlock.objects.filter(user=self.request.user)

class UserDevicesView(generics.ListCreateAPIView):
    """Kullanıcı cihazları listeleme ve ekleme"""
    permission_classes = (IsAuthenticated,)
    serializer_class = UserDeviceSerializer

    def get_queryset(self):
        return UserDevice.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserDeviceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Kullanıcı cihazı detay, güncelleme ve silme"""
    permission_classes = (IsAuthenticated,)
    serializer_class = UserDeviceSerializer

    def get_queryset(self):
        return UserDevice.objects.filter(user=self.request.user)

class UserAchievementsView(generics.ListAPIView):
    """Kullanıcı başarıları listeleme"""
    permission_classes = (IsAuthenticated,)
    serializer_class = AchievementSerializer

    def get_queryset(self):
        return Achievement.objects.filter(userachievement__user=self.request.user)

class AchievementDetailView(generics.RetrieveAPIView):
    """Başarı detayı görüntüleme"""
    queryset = Achievement.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = AchievementSerializer

class PremiumSubscriptionView(views.APIView):
    """Premium üyelik başlatma"""
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        # Ödeme işlemleri burada yapılacak
        user = request.user
        user.is_premium = True
        user.premium_until = None  # Ödeme süresine göre ayarlanacak
        user.save()
        return Response({'detail': 'Premium üyeliğiniz başarıyla başlatıldı.'})

class PremiumCancellationView(views.APIView):
    """Premium üyelik iptali"""
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        if not user.is_premium:
            return Response(
                {'detail': 'Premium üyeliğiniz bulunmuyor.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.is_premium = False
        user.premium_until = None
        user.save()
        return Response({'detail': 'Premium üyeliğiniz iptal edildi.'})

class PremiumStatusView(views.APIView):
    """Premium üyelik durumu"""
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        return Response({
            'is_premium': user.is_premium,
            'premium_until': user.premium_until
        }) 