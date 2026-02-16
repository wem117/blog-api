import logging
from typing import Any, Dict
from django.db.models import Model
from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, UserSerializer

logger = logging.getLogger(__name__)

class LoggingTokenObtainPairView(TokenObtainPairView):
    """Custom TokenObtainPairView with logging for login attempts."""
    throttle_scope = 'login'
    
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        email = request.data.get('email', 'unknown')
        logger.info('Login attempt for email: %s', email)
        response = super().post(request, *args, **kwargs)
        logger.info('Login success for email: %s', email)
        return response

class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    throttle_scope = 'register'

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        logger.info('Registration attempt for email: %s', request.data.get('email'))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        logger.info('User registered successfully: %s', user.email)
        return Response({
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

