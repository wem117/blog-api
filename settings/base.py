from pathlib import Path
from .conf import BLOG_SECRET_KEY, BLOG_DEBUG, BLOG_ALLOWED_HOSTS, BLOG_REDIS_URL

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = BLOG_SECRET_KEY
DEBUG = BLOG_DEBUG
ALLOWED_HOSTS = BLOG_ALLOWED_HOSTS

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'apps.blog',
    'apps.users',
    'rest_framework',
    'rest_framework_simplejwt',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'settings.urls' 

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'settings.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {'()': 'django.utils.log.RequireDebugTrue'},
    },
    'formatters': {
        'simple': {'format': '{levelname} {message}', 'style': '{'},
        'verbose': {'format': '{asctime} {levelname} {name} {module} {message}', 'style': '{'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'simple', 'level': 'DEBUG'},
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/app.log', 'formatter': 'verbose', 'level': 'WARNING',
            'maxBytes': 5*1024*1024, 'backupCount': 3
        },
        'debug_requests': {
            'class': 'logging.FileHandler', 'filename': 'logs/debug_requests.log',
            'formatter': 'verbose', 'filters': ['require_debug_true']
        },
    },
    'loggers': {
        'apps.users': {'handlers': ['console', 'file'], 'level': 'DEBUG', 'propagate': False},
        'apps.blog': {'handlers': ['console', 'file'], 'level': 'DEBUG', 'propagate': False},
        'django.request': {'handlers': ['file', 'debug_requests'], 'level': 'DEBUG', 'propagate': False},
    },
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'register': '5/minute',
        'login': '10/minute',
        'post_create': '20/minute',
    },
    'EXCEPTION_HANDLER': 'apps.blog.views.minimal_429_handler',
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": BLOG_REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.User'
