"""
Configurações de produção para o projeto Nossa Grana
"""

from .settings import *
import os
from decouple import config

# Sobrescrever configurações para produção
DEBUG = False

# Hosts permitidos em produção
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

# Database PostgreSQL para produção
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB', default='nossa_grana_prod'),
        'USER': config('POSTGRES_USER', default='nossa_grana_user'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': config('DB_HOST', default='db'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'connect_timeout': 60,
        },
        'CONN_MAX_AGE': 600,
    }
}

# Redis Cache para produção
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://redis:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'TIMEOUT': 1800,
        'KEY_PREFIX': 'nossa_grana_prod',
    },
    'sessions': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://redis:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 3600,
        'KEY_PREFIX': 'sessions_prod',
    }
}

# Configurações de sessão com Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'

# CORS restritivo para produção
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS', 
    default='https://localhost,https://127.0.0.1',
    cast=lambda v: [s.strip() for s in v.split(',')]
)
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CORS_PREFLIGHT_MAX_AGE = 86400  # 24 horas
CORS_ALLOW_PRIVATE_NETWORK = False
CORS_EXPOSE_HEADERS = ['Content-Length', 'X-CSRFToken']

# Headers CORS mais restritivos
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'origin',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]

# Configurações de segurança SSL/TLS robustas para produção
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS (HTTP Strict Transport Security) - 2 anos para produção
SECURE_HSTS_SECONDS = 63072000  # 2 anos
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# SSL Redirect e configurações de proxy
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Configurações SSL avançadas
SECURE_SSL_HOST = None  # Força SSL para host específico se necessário
SECURE_REDIRECT_EXEMPT = [r'^health/$', r'^status/$', r'^metrics/$']  # Health checks e métricas

# Content Security Policy para produção
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)  # Sem 'unsafe-inline' em produção
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")  # Necessário para alguns frameworks CSS
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'", "https:")
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'",)
CSP_UPGRADE_INSECURE_REQUESTS = True

# Cookies seguros para produção
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'  # Mais restritivo em produção
CSRF_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_NAME = 'nossa_grana_prod_sessionid'
CSRF_COOKIE_NAME = 'nossa_grana_prod_csrftoken'

# Headers de segurança avançados
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

# Permissions Policy (Feature Policy) para produção
PERMISSIONS_POLICY = {
    'geolocation': [],
    'microphone': [],
    'camera': [],
    'payment': [],
    'usb': [],
    'magnetometer': [],
    'gyroscope': [],
    'accelerometer': [],
    'autoplay': [],
    'encrypted-media': [],
    'fullscreen': [],
    'picture-in-picture': [],
}

# Configurações de TLS/SSL para servidor web (nginx/apache)
SSL_PROTOCOLS = ['TLSv1.2', 'TLSv1.3']
SSL_CIPHER_SUITES = [
    'ECDHE-ECDSA-AES256-GCM-SHA384',
    'ECDHE-RSA-AES256-GCM-SHA384',
    'ECDHE-ECDSA-CHACHA20-POLY1305',
    'ECDHE-RSA-CHACHA20-POLY1305',
    'ECDHE-ECDSA-AES128-GCM-SHA256',
    'ECDHE-RSA-AES128-GCM-SHA256',
]

# Configurações de arquivos estáticos para produção
STATIC_ROOT = '/app/staticfiles'
MEDIA_ROOT = '/app/media'

# WhiteNoise para servir arquivos estáticos
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Configurações de email para produção localhost
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Para desenvolvimento
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=1025, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='nossagrana@localhost')

# Celery para produção
CELERY_BROKER_URL = config('REDIS_URL', default='redis://redis:6379/2')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://redis:6379/3')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Logging otimizado para produção
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"level": "{levelname}", "time": "{asctime}", "module": "{module}", "message": "{message}"}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/nossa_grana.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'json',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/security.log',
            'maxBytes': 10485760,
            'backupCount': 5,
            'formatter': 'json',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/errors.log',
            'maxBytes': 10485760,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'financial_security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'nossa_grana': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Rate limiting mais restritivo para produção
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '50/hour',
    'user': '500/hour',
    'financial': '200/hour',
    'login': '10/hour',
    'password_reset': '5/hour',
    'registration': '3/hour',
}

# Configurações de segurança adicionais para sessões
SESSION_COOKIE_AGE = 1800  # 30 minutos em produção
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True
CSRF_COOKIE_AGE = 1800  # 30 minutos

# Configurações de performance
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB