from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# API URL desenleri
api_patterns = [
    path('accounts/', include('allauth.urls')),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('accounts/', include('apps.accounts.urls')),
    path('movies/', include('apps.movies.urls')),
    path('games/', include('apps.games.urls')),
    path('social/', include('apps.social.urls')),
]

# API dokümantasyonu için schema view
schema_view = get_schema_view(
    openapi.Info(
        title="CineSocial API",
        default_version='v1',
        description="CineSocial platformu için REST API dokümantasyonu",
        terms_of_service="https://www.cinesocial.com/terms/",
        contact=openapi.Contact(email="contact@cinesocial.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
    patterns=[path('api/v1/', include(api_patterns))],
)

urlpatterns = [
    # url(r'^__debug__/', include(debug_toolbar.urls)), give thsis as path
    path('__debug__/', include('debug_toolbar.urls')),
            
    # Admin paneli
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/v1/', include(api_patterns)),
    
    # API dokümantasyonu
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Prometheus metrikleri
    path('', include('django_prometheus.urls')),
]

# Debug modunda medya dosyaları için URL desenleri
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 