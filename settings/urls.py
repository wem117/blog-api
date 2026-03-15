"""
Blog API URLs.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from apps.users.views import AuthViewSet, LoggingTokenObtainPairView, UpdateLangView, UpdateTimeZoneView, DocumentedTokenRefreshView
from apps.blog.views import PostViewSet, StatsView

router = DefaultRouter()
router.register(r'auth/register', AuthViewSet, basename='register')
router.register(r'posts', PostViewSet, basename='post')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/token/', LoggingTokenObtainPairView.as_view(), name='token_obtain'),
    path('api/auth/token/refresh/', DocumentedTokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/update-lang/', UpdateLangView.as_view(), name='update-lang'),
    path('api/users/update-timezone/', UpdateTimeZoneView.as_view(), name='update-timezone'),
    path('api/stats/', StatsView.as_view(), name='stats'),
    
    # Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
