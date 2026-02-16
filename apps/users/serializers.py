import logging
from typing import Any, Dict
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()
logger = logging.getLogger(__name__)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'avatar', 'password', 'password_confirm')

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        if attrs['password'] != attrs['password_confirm']:
            logger.warning('Password mismatch for user registration: %s', attrs.get('email'))
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
    
    def create(self, validated_data: Dict[str, Any]) -> User:
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        logger.info('User created: %s', user.email)
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'avatar')