from pathlib import Path
import dj_database_url
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

SOCIALACCOUNT_LOGIN_ON_GET = True

ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"

# ================== ENVIRONMENT ==================
# ENVIRONMENT: local | production
ENVIRONMENT = os.environ.get("ENVIRONMENT", "local")


# Local thì load .env, Railway thì không cần (Railway inject env trực tiếp)
if ENVIRONMENT == "local":
    load_dotenv(os.path.join(BASE_DIR, ".env"))

# Secret key
SECRET_KEY = os.environ.get("SECRET_KEY")

# DEBUG: set qua env, mặc định True cho local
DEBUG = os.environ.get("DEBUG", "True") == "True"

# ALLOWED_HOSTS: đọc từ env, dạng: "localhost,127.0.0.1,api.hsonspace.id.vn"
raw_hosts = os.environ.get("ALLOWED_HOSTS", "")
if raw_hosts:
    ALLOWED_HOSTS = [h.strip() for h in raw_hosts.split(",") if h.strip()]
else:
    # fallback cho local
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]


INSTALLED_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Thứ ba
    'rest_framework',
    'django_filters',
    'corsheaders',
    'rest_framework.authtoken',

    # Auth
    'allauth',
    
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',

    'dj_rest_auth',
    'dj_rest_auth.registration',

    # App của bạn
    'todo',
]


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Luôn ở trên cùng
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Thêm cho allauth
]

ROOT_URLCONF = 'djangostart.urls'

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

WSGI_APPLICATION = 'djangostart.wsgi.application'


# ================== DATABASE ==================
DATABASES = {
    "default": dj_database_url.config(
        
        env="DATABASE_URL",
        conn_max_age=0,  # dev: mỗi request xong là đóng kết nối
    )
}

DATABASES['default']['CONN_MAX_AGE'] = 300  # persistent connections
DATABASES['default']["CONN_HEALTH_CHECKS"] = True


# ================== PASSWORD VALIDATORS ==================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ================== I18N ==================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Ho_Chi_Minh'  # giờ Việt Nam
USE_I18N = True
USE_TZ = True  # lưu UTC


STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ================== CACHE ==================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}


# ================== CORS / CSRF ==================
# Frontend chính (local hoặc production)
FRONTEND_ORIGIN = os.environ.get(
    "FRONTEND_ORIGIN",
    "http://localhost:3000",  # mặc định local
)

# URL frontend của m
FRONTEND_URL = "http://localhost:3000"  # local
# hoặc khi lên prod:
# FRONTEND_URL = "https://hsonspace.id.vn"

# Sau khi login xong, Allauth sẽ redirect về đây
LOGIN_REDIRECT_URL = FRONTEND_URL
LOGOUT_REDIRECT_URL = FRONTEND_URL
ACCOUNT_LOGOUT_REDIRECT_URL = FRONTEND_URL


# Backend origin – dùng cho CSRF_TRUSTED_ORIGINS (Railway hoặc api.hsonspace.id.vn)
BACKEND_ORIGIN = os.environ.get(
    "BACKEND_ORIGIN", 
    "http://127.0.0.1:8000"
    )

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://hsonspace.id.vn",
]

# Thêm FRONTEND_ORIGIN nếu khác default
if FRONTEND_ORIGIN and FRONTEND_ORIGIN not in CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS.append(FRONTEND_ORIGIN)

# Cho phép backend tự gọi chính nó (nếu cần)
if BACKEND_ORIGIN and BACKEND_ORIGIN not in CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS.append(BACKEND_ORIGIN)

# Nếu cần thêm origin khác thì set EXTRA_CORS_ORIGINS="https://foo,https://bar" trong env
extra_cors = os.environ.get("EXTRA_CORS_ORIGINS", "")
if extra_cors:
    CORS_ALLOWED_ORIGINS.extend(
        [o.strip() for o in extra_cors.split(",") if o.strip()]
    )

# Cho phép credentials (cookies, authorization headers)
CORS_ALLOW_CREDENTIALS = True

# Cho phép tất cả headers
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

# CSRF Configuration
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://hsonspace.id.vn",
    "https://api.hsonspace.id.vn",
]

# Thêm origins từ env
for origin in [FRONTEND_ORIGIN, BACKEND_ORIGIN]:
    if origin and origin.startswith("http") and origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)

extra_csrf = os.environ.get("EXTRA_CSRF_ORIGINS", "")
if extra_csrf:
    CSRF_TRUSTED_ORIGINS.extend(
        [o.strip() for o in extra_csrf.split(",") if o.strip()]
    )


# ================== REST FRAMEWORK ==================
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

SITE_ID = 1


EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# ================== ALLAUTH / DJ-REST-AUTH ==================
# 1. Cú pháp mới cho allauth
ACCOUNT_LOGIN_METHODS = ['username']
ACCOUNT_SIGNUP_FIELDS = ['username', 'email']  # 'password' được ngầm định

# 2. Cú pháp cũ cho dj-rest-auth (bắt buộc, dù có warnings)
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_UNIQUE_EMAIL = False
SOCIALACCOUNT_AUTO_SIGNUP = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False  # Rất quan trọng

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        # "APP": {
        #     "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
        #     "secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
        #     "key": "",
        # },
    },
    "github": {
        # "APP": {
        #     "client_id": os.environ.get("GITHUB_CLIENT_ID"),
        #     "secret": os.environ.get("GITHUB_CLIENT_SECRET"),
        #     "key": ""
        # }
    },
}

if DEBUG:
    FRONTEND_URL = "http://localhost:3000"
else:
    FRONTEND_URL = "https://hsonspace.id.vn"

LOGIN_REDIRECT_URL = "/accounts/redirect-after-login/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/accounts/redirect-after-login/"
