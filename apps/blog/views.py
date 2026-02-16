import logging
from typing import Any, List, Optional
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from django.db.models import QuerySet
from .models import Post
from .serializer import PostSerializer, CommentSerializer
from .permission import IsAuthorOrReadOnly

import json
from django_redis import get_redis_connection
from rest_framework.views import exception_handler

def minimal_429_handler(exc, context):
    response = exception_handler(exc, context)
    if response and response.status_code == 429:
        response.data = {"detail": "Too many requests. Try again later."}
    return response

class PostViewSet(viewsets.ModelViewSet):
    queryset: QuerySet[Post] = Post.objects.filter(status='published')
    serializer_class = PostSerializer
    lookup_field = 'slug'
    throttle_scope = 'post_create'


    def get_permissions(self) -> List[permissions.BasePermission]:
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAuthorOrReadOnly()]

    def perform_create(self, serializer: PostSerializer) -> None:
        serializer.save(author=self.request.user)
        logger.info('Post created by user: %s', self.request.user.email)

    @action(detail=True, methods=['get', 'post'], url_path='comments')
    def comments(self, request: Request, slug: Optional[str] = None) -> Response:
        post = self.get_object()
        
        if request.method == 'GET':
            comments = post.comments.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)

        if request.method == 'POST':
            serializer = CommentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(author=request.user, post=post)
            
            # Pub/Sub (Ultra-minimal)
            get_redis_connection("default").publish('comments', json.dumps(serializer.data))
            
            logger.info('Comment added to post %s by %s', post.slug, request.user.email)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        logger.info('POST created: %s', serializer.instance.slug)

    def perform_destroy(self, instance):
        logger.info('POST deleted: %s', instance.slug)
        instance.delete()