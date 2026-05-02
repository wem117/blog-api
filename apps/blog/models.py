from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(_('name'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), unique=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self) -> str:
        return self.name

class Tag(models.Model):
    name = models.CharField(_('name'), max_length=50, unique=True)
    slug = models.SlugField(_('slug'), unique=True)

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    def __str__(self) -> str:
        return self.name

class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        PUBLISHED = 'published', _('Published')

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        verbose_name=_('author')
    )
    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(_('slug'), unique=True)
    body = models.TextField(_('body'))
    
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_('category')
    )
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_('tags'))
    
    status = models.CharField(
        _('status'),
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')

    def __str__(self) -> str:
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='comments',
        verbose_name=_('post')
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        verbose_name=_('author')
    )
    body = models.TextField(_('body'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')

    def __str__(self) -> str:
        return f"Comment by {self.author} on {self.post}"