from decouple import config

BLOG_SECRET_KEY = config('BLOG_SECRET_KEY', default='django-insecure-default')
BLOG_DEBUG = config('BLOG_DEBUG', default=True, cast=bool)
BLOG_ENV_ID = config('BLOG_ENV_ID', default='local')
BLOG_ALLOWED_HOSTS = config('BLOG_ALLOWED_HOSTS', default='', cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])
BLOG_REDIS_URL = config('BLOG_REDIS_URL', default='redis://127.0.0.1:6379/1')

# Add other variables as needed
