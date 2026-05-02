import logging
from django.utils import timezone, formats
from rest_framework import serializers
from .models import Post, Comment, Category, Tag

logger = logging.getLogger(__name__)

from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.email')
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'author', 'body', 'created_at')

    @extend_schema_field(OpenApiTypes.STR)
    def get_created_at(self, obj):

        local_dt = timezone.localtime(obj.created_at)
        return formats.date_format(local_dt, format='DATETIME_FORMAT', use_l10n=True)

class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.email')
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'slug', 'author', 'body', 'category', 'tags', 'status', 'created_at', 'updated_at')

    @extend_schema_field(OpenApiTypes.STR)
    def get_created_at(self, obj):

        local_dt = timezone.localtime(obj.created_at)
        return formats.date_format(local_dt, format='DATETIME_FORMAT', use_l10n=True)

    @extend_schema_field(OpenApiTypes.STR)
    def get_updated_at(self, obj):

        local_dt = timezone.localtime(obj.updated_at)
        return formats.date_format(local_dt, format='DATETIME_FORMAT', use_l10n=True)