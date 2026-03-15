import logging
import json
from typing import Any, List, Optional
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from django.db.models import QuerySet
from django.core.cache import cache
from django.utils import translation
from django_redis import get_redis_connection
from rest_framework.views import exception_handler
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, extend_schema_view
from drf_spectacular.types import OpenApiTypes

from .models import Post
from .serializer import PostSerializer, CommentSerializer
from .permission import IsAuthorOrReadOnly
import httpx
import asyncio
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

def minimal_429_handler(exc, context):
    response = exception_handler(exc, context)
    if response and response.status_code == 429:
        response.data = {"detail": "Too many requests. Try again later."}
    return response

@extend_schema_view(
    list=extend_schema(
        summary="List posts",
        description="Get published posts. Cached by lang.",
        parameters=[OpenApiParameter("lang", OpenApiTypes.STR, OpenApiParameter.QUERY, description="Lang code")],
        responses={200: PostSerializer(many=True), 429: None},
        tags=['Posts']
    ),
    retrieve=extend_schema(
        summary="Get post",
        description="Post details by slug.",
        responses={200: PostSerializer, 404: None, 429: None},
        tags=['Posts']
    ),
    create=extend_schema(
        summary="New post",
        description="Creates post. Clears cache.",
        responses={201: PostSerializer, 400: None, 401: None, 403: None, 429: None},
        tags=['Posts'],
        examples=[OpenApiExample('Post Create', value={'title': 'Hi', 'body': 'Bye', 'category': 1, 'status': 'published'})]
    ),
    update=extend_schema(summary="Edit post", description="Updates post. Clears cache.", tags=['Posts']),
    partial_update=extend_schema(summary="Patch post", description="Patches post. Clears cache.", tags=['Posts']),
    destroy=extend_schema(summary="Del post", description="Deletes post. Clears cache.", tags=['Posts']),
)

class PostViewSet(viewsets.ModelViewSet):

    queryset: QuerySet[Post] = Post.objects.filter(status='published')
    serializer_class = PostSerializer
    lookup_field = 'slug'
    throttle_scope = 'post_create'


    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        lang = translation.get_language()
        cache_key = f"post_list_{lang}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60*15) # 15 min
        return response

    def get_permissions(self) -> List[permissions.BasePermission]:
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAuthorOrReadOnly()]

    def _clear_cache(self):
        for lang in ['en', 'ru', 'kk']:
            cache.delete(f"post_list_{lang}")

    def perform_create(self, serializer: PostSerializer) -> None:
        serializer.save(author=self.request.user)
        self._clear_cache()
        logger.info('Post created by user: %s', self.request.user.email)

    def perform_update(self, serializer: PostSerializer) -> None:
        serializer.save()
        self._clear_cache()
        logger.info('Post updated: %s', serializer.instance.slug)

    def perform_destroy(self, instance: Post) -> None:
        self._clear_cache()
        logger.info('Post deleted: %s', instance.slug)
        instance.delete()

    @extend_schema(
        methods=['GET'],
        summary="Get comms",
        description="Post comments.",
        responses={200: CommentSerializer(many=True)},
        tags=['Comments']
    )
    @extend_schema(
        methods=['POST'],
        summary="Add comm",
        description="Add comment. Pubs to Redis.",
        request=CommentSerializer,
        responses={21: CommentSerializer, 400: None, 401: None},
        tags=['Comments'],
        examples=[
            OpenApiExample('Comm', value={'body': 'Nice'})
        ]
    )

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
            
            get_redis_connection("default").publish('comments', json.dumps(serializer.data))
            
            logger.info('Comment added to post %s by %s', post.slug, request.user.email)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class StatsView(APIView):
    permission_classes = [permissions.AllowAny]

    async def fetch_external_data(self, client):
        try:
            response = await client.get("https://api.github.com/zen", timeout=5.0)
            return response.text
        except Exception:
            return "Keep it simple."

    @extend_schema(
        summary="Stats",
        description="Post/comm counts + github zen.",
        tags=['Stats'],
        responses={200: OpenApiTypes.OBJECT},
        examples=[
            OpenApiExample('Stats', value={
                'posts_count': 10,
                'comments_count': 50,
                'external_message': 'Zen'
            })
        ]
    )

    async def get(self, request):
        posts_count = await asyncio.to_thread(Post.objects.count)
        comments_count = await asyncio.to_thread(Post.objects.filter(status='published').count) # Just an example
        
        async with httpx.AsyncClient() as client:
            external_message = await self.fetch_external_data(client)

        return Response({
            'posts_count': posts_count,
            'comments_count': comments_count,
            'external_message': external_message
        })