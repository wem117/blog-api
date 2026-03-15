import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.blog.models import Category, Post, Tag, Comment
from django.utils.text import slugify

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed database with test data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        
        # 1. Users
        users = []
        for i in range(5):
            email = f'user{i}@example.com'
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    email=email,
                    password='password123',
                    first_name=f'User{i}',
                    last_name='Test',
                    preferred_language=random.choice(['en', 'ru', 'kk']),
                    user_timezone=random.choice(['UTC', 'Asia/Almaty', 'Europe/Moscow'])
                )
                users.append(user)
            else:
                users.append(User.objects.get(email=email))

        # 2. Categories 
        categories_data = [
            {'en': 'Technology', 'ru': 'Технологии', 'kk': 'Технология'},
            {'en': 'Life', 'ru': 'Жизнь', 'kk': 'Өмір'},
            {'en': 'Python', 'ru': 'Пайтон', 'kk': 'Пайтон'},
        ]
        categories = []
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                slug=slugify(cat_data['en']),
                defaults={'name_en': cat_data['en'], 'name_ru': cat_data['ru'], 'name_kk': cat_data['kk']}
            )
            categories.append(cat)

        # 3. Tags
        tags_data = ['news', 'tutorial', 'daily', 'ai']
        tags = []
        for name in tags_data:
            tag, created = Tag.objects.get_or_create(
                name=name,
                defaults={'slug': slugify(name)}
            )
            tags.append(tag)

        # 4. Posts
        for i in range(15):
            title = f'Post {i}'
            if not Post.objects.filter(title=title).exists():
                post = Post.objects.create(
                    title=title,
                    slug=slugify(title),
                    body=f'This is the body of post {i}. It contains some text.',
                    author=random.choice(users),
                    category=random.choice(categories),
                    status=random.choice(['published', 'draft'])
                )
                post.tags.add(*random.sample(tags, 2))
                
                # 5. Comments
                for j in range(random.randint(1, 4)):
                    Comment.objects.create(
                        post=post,
                        author=random.choice(users),
                        body=f'Comment {j} on post {i}'
                    )

        self.stdout.write(self.style.SUCCESS('Successfully seeded data.'))
