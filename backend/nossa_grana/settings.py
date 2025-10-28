"""
Django settings for nossa_grana project.
"""

from pathlib import Path
from decouple import config
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# Configuração condicional de ALLOWED_HOSTS
if DEBUG:
    ALLOWED_HOSTS = ['*']  # Desenvolvimento: permite qualquer host
else:
    ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
]

LOCAL_APPS = [
    'accounts',
    'transactions',
    'budgets',
    'goals',
    'reports',
    'financial_accounts',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'middleware.security.SecurityHeadersMiddleware',  # Headers de segurança personalizados
    'middleware.encoding.UTF8EncodingMiddleware',
    'middleware.encoding.JSONResponseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'middleware.security.SSLRedirectMiddleware',  # SSL redirect personalizado
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'nossa_grana.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'nossa_grana.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 30,
        },
        'CONN_MAX_AGE': 600,
    }
}

# Database Transaction Settings
DATABASE_ROUTERS = []
AUTOCOMMIT = True
DATABASE_OPTIONS = {
    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
    'charset': 'utf8mb4',
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Encoding Configuration
DEFAULT_CHARSET = 'utf-8'
FILE_CHARSET = 'utf-8'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'financial': '500/hour'
    },
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'UNICODE_JSON': True,
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# CORS Settings condicionais
if DEBUG:
    # Desenvolvimento: permite todas as origens
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]
else:
    # Produção: usa variáveis de ambiente
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = config(
        'CORS_ALLOWED_ORIGINS', 
        default='https://localhost,https://127.0.0.1',
        cast=lambda v: [s.strip() for s in v.split(',')]
    )

CORS_ALLOW_CREDENTIALS = True

# Configurações CORS avançadas
CORS_PREFLIGHT_MAX_AGE = 86400  # 24 horas
CORS_ALLOW_PRIVATE_NETWORK = False  # Bloqueia requests de redes privadas

if not DEBUG:
    # Em produção, ser mais restritivo
    CORS_ALLOW_CREDENTIALS = True
    CORS_EXPOSE_HEADERS = ['Content-Length', 'X-CSRFToken']
else:
    # Em desenvolvimento, mais flexível
    CORS_ALLOW_CREDENTIALS = True

# Headers permitidos
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Métodos permitidos
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'nossa-grana-cache',
        'TIMEOUT': 1800,  # 30 minutos
        'OPTIONS': {
            'MAX_ENTRIES': 5000,
            'CULL_FREQUENCY': 3,
        }
    },
    'sessions': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'sessions-cache',
        'TIMEOUT': 3600,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Cache para sessões
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'sessions'

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'nossa_grana.log',
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'financial_security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'nossa_grana': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
    },
}

# Security Settings
if not DEBUG:
    # SSL/TLS Security - Configurações robustas para produção
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # HSTS (HTTP Strict Transport Security) - 2 anos
    SECURE_HSTS_SECONDS = 63072000  # 2 anos
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # SSL Redirect e Proxy
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Cookies seguros
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Configurações SSL avançadas
    SECURE_SSL_HOST = None
    SECURE_REDIRECT_EXEMPT = [r'^health/$', r'^status/$']  # Health checks
    
    # Content Security Policy básica
    CSP_DEFAULT_SRC = ("'self'",)
    CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
    CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
    CSP_IMG_SRC = ("'self'", "data:", "https:")
    CSP_FONT_SRC = ("'self'", "https:")
    CSP_CONNECT_SRC = ("'self'",)
    CSP_FRAME_ANCESTORS = ("'none'",)
    
else:
    # Para desenvolvimento com HTTPS local
    USE_HTTPS = config('USE_HTTPS', default=False, cast=bool)
    SECURE_SSL_REDIRECT = USE_HTTPS
    
    if USE_HTTPS:
        SESSION_COOKIE_SECURE = True
        CSRF_COOKIE_SECURE = True
        SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
        # HSTS mais brando para desenvolvimento
        SECURE_HSTS_SECONDS = 3600  # 1 hora
        SECURE_HSTS_INCLUDE_SUBDOMAINS = False
        SECURE_HSTS_PRELOAD = False

# Session Security
SESSION_COOKIE_AGE = 3600  # 1 hora
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_NAME = 'nossa_grana_sessionid'  # Nome customizado
SESSION_SAVE_EVERY_REQUEST = True  # Renova sessão a cada request

# CSRF Security
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_NAME = 'nossa_grana_csrftoken'  # Nome customizado
CSRF_USE_SESSIONS = False  # Mantém no cookie para SPA
CSRF_COOKIE_AGE = 3600  # 1 hora

# SameSite Policy
if not DEBUG:
    SESSION_COOKIE_SAMESITE = 'Strict'  # Mais restritivo em produção
    CSRF_COOKIE_SAMESITE = 'Strict'
else:
    SESSION_COOKIE_SAMESITE = 'Lax'  # Mais flexível em desenvolvimento
    CSRF_COOKIE_SAMESITE = 'Lax'

# Headers de segurança avançados
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

if not DEBUG:
    # Políticas de segurança para produção
    SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
    
    # Permissions Policy (Feature Policy)
    PERMISSIONS_POLICY = {
        'geolocation': [],
        'microphone': [],
        'camera': [],
        'payment': [],
        'usb': [],
        'magnetometer': [],
        'gyroscope': [],
        'accelerometer': [],
    }
    
    # Configurações SSL de cipher suites (se usando nginx/apache)
    SSL_CIPHER_SUITES = [
        'ECDHE-RSA-AES256-GCM-SHA384',
        'ECDHE-RSA-AES128-GCM-SHA256',
        'ECDHE-RSA-AES256-SHA384',
        'ECDHE-RSA-AES128-SHA256',
    ]