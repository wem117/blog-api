import logging
from typing import Any, Dict
from django.db.models import Model
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .serializers import (
    RegisterSerializer, UserSerializer, UpdateLangSerializer, UpdateTimeZoneSerializer
)
from .email_service import send_welcome_email

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Reg user",
        description="Creates user + welcome email.",
        request=RegisterSerializer,
        responses={201: UserSerializer, 400: None, 429: None},
        tags=['Auth'],


        examples=[
            OpenApiExample(
                'Registration Example',
                value={
                    'email': 'user@example.com',
                    'first_name': 'Miras',
                    'last_name': 'Zhumatayev',
                    'password': 'password123',
                    'password_confirm': 'password123',
                    'preferred_language': 'kk',
                    'user_timezone': 'Asia/Almaty'
                }
            )
        ]
    )
    def post(self, request):

        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_welcome_email(user)
            return Response({'message': 'User registered'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateLangView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Set lang",
        description="Updates lang pref.",
        request=UpdateLangSerializer,
        responses={200: OpenApiExample('Success', value={'message': 'Updated'}), 400: None, 401: None, 403: None, 429: None},
        tags=['Auth'],


        examples=[
            OpenApiExample('Language Update', value={'preferred_language': 'kk'})
        ]
    )
    def patch(self, request):
        serializer = UpdateLangSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Updated'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateTimeZoneView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Set tz",
        description="Updates user timezone.",
        request=UpdateTimeZoneSerializer,
        responses={200: OpenApiExample('Success', value={'message': 'Updated'}), 400: None, 401: None, 403: None, 429: None},
        tags=['Auth'],


        examples=[
            OpenApiExample('Timezone Update', value={'user_timezone': 'Asia/Almaty'})
        ]
    )
    def patch(self, request):
        serializer = UpdateTimeZoneSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Updated'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            
class LoggingTokenObtainPairView(TokenObtainPairView):
    
    throttle_scope = 'login'
    
    @extend_schema(
        summary="Login",
        description="Get JWT tokens.",
        tags=['Auth'],
        responses={200: OpenApiTypes.OBJECT, 401: None, 429: None},

        examples=[
            OpenApiExample('Login Example', value={'email': 'user@example.com', 'password': 'password123'})
        ]
    )
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

    @extend_schema(
        summary="Register user",
        description="Alternative registration. Returns tokens immediately.",
        tags=['Auth'],
        responses={201: None, 400: None, 429: None}
    )

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        logger.info('Registration attempt for email: %s', request.data.get('email'))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

@extend_schema(
    summary="Refresh",
    description="Get new access token.",
    tags=['Auth'],
    responses={200: OpenApiTypes.OBJECT, 401: None, 429: None}
)
class DocumentedTokenRefreshView(TokenRefreshView):
    pass
