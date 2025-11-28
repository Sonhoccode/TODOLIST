from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

SOCIALACCOUNT_LOGIN_ON_GET = True

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
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}


# ================== PASSWORD VALIDATORS ==================
# Đang để trống để test cho dễ
AUTH_PASSWORD_VALIDATORS = []


# ================== I18N ==================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Ho_Chi_Minh'  # giờ Việt Nam
USE_I18N = True
USE_TZ = True  # lưu UTC


STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ================== CORS / CSRF ==================
# Frontend chính (local hoặc production)
FRONTEND_ORIGIN = os.environ.get(
    "FRONTEND_ORIGIN",
    "http://localhost:3000",  # mặc định local
)

# Backend origin – dùng cho CSRF_TRUSTED_ORIGINS (Railway hoặc api.hsonspace.id.vn)
BACKEND_ORIGIN = os.environ.get("BACKEND_ORIGIN")  # vd: "https://api.hsonspace.id.vn"

CORS_ALLOWED_ORIGINS = []

# Cho phép frontend gọi vào
if FRONTEND_ORIGIN:
    CORS_ALLOWED_ORIGINS.append(FRONTEND_ORIGIN)

# Thêm các port local thường dùng
CORS_ALLOWED_ORIGINS.extend([
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
])

# Cho phép backend tự gọi chính nó (nếu cần)
if BACKEND_ORIGIN:
    CORS_ALLOWED_ORIGINS.append(BACKEND_ORIGIN)

# Nếu cần thêm origin khác thì set EXTRA_CORS_ORIGINS="https://foo,https://bar" trong env
extra_cors = os.environ.get("EXTRA_CORS_ORIGINS", "")
if extra_cors:
    CORS_ALLOWED_ORIGINS.extend(
        [o.strip() for o in extra_cors.split(",") if o.strip()]
    )

# Nếu sau này cần cookie / session thì bật cái này
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = []

# Cả frontend và backend (nếu có https://...) đều được trust
for origin in [FRONTEND_ORIGIN, BACKEND_ORIGIN]:
    if origin and origin.startswith("http"):
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
}

SITE_ID = 1


# ================== EMAIL ==================
# Local: in mail ra console; Production: dùng SMTP qua env (Zoho / Gmail đều được)
if DEBUG and ENVIRONMENT == "local":
    # local / debug: in mail ra console cho dễ test
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    # production: gửi thật qua SMTP (m set trong env)
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.zoho.com")
    EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
    EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")      # vd: adminspace@hsonspace.id.vn
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")  # app password
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# ================== ALLAUTH / DJ-REST-AUTH ==================
# 1. Cú pháp mới cho allauth
ACCOUNT_LOGIN_METHODS = ['username']
ACCOUNT_SIGNUP_FIELDS = ['username', 'email']  # 'password' được ngầm định

# 2. Cú pháp cũ cho dj-rest-auth (bắt buộc, dù có warnings)
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False  # Rất quan trọng

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
            "secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
            "key": ""
        }
    },
    "github": {
        "APP": {
            "client_id": os.environ.get("GITHUB_CLIENT_ID"),
            "secret": os.environ.get("GITHUB_CLIENT_SECRET"),
            "key": ""
        }
    },
}
