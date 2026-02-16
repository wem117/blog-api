import logging
from rest_framework import serializers
from .models import Post, Comment, Category, Tag

logger = logging.getLogger(__name__)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.email')

    class Meta:
        model = Comment
        fields = ('id', 'author', 'body', 'created_at')

class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.email')
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'title', 'slug', 'author', 'body', 'category', 'tags', 'status', 'created_at', 'updated_at')