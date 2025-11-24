from pathlib import Path
import os
from dotenv import load_dotenv 

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- TẢI BIẾN MÔI TRƯỜNG ---
load_dotenv(os.path.join(BASE_DIR, '.env'))


# --- LẤY BIẾN TỪ .ENV ---
SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = True
ALLOWED_HOSTS = []


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
    'allauth.account.middleware.AccountMiddleware', # Thêm cho allauth
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


# --- CẤU HÌNH DATABASE (ĐỌC TỪ .ENV) ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}


# --- VÔ HIỆU HÓA BỘ LỌC MẬT KHẨU (ĐỂ TEST) ---
AUTH_PASSWORD_VALIDATORS = []


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Ho_Chi_Minh' # <-- Đổi sang giờ Việt Nam
USE_I18N = True
USE_TZ = True # Giữ True để lưu giờ UTC (chuẩn)


STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- CẤU HÌNH CORS (CHO PHÉP REACT) ---
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000", # Port React của bạn
    "http://127.0.0.1:3000",
]

# --- CẤU HÌNH REST FRAMEWORK (DÙNG TOKEN AUTH) ---
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ]
}

# --- CẤU HÌNH ALLAUTH (ĐỂ TẮT XÁC THỰC EMAIL) ---
SITE_ID = 1
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' 

# 1. Cài đặt cho allauth (Cú pháp MỚI, sửa lỗi CRITICAL và WARNINGS)
ACCOUNT_LOGIN_METHODS = ['username']
ACCOUNT_SIGNUP_FIELDS = ['username', 'email'] # 'password' được ngầm định

# 2. Cài đặt cho dj-rest-auth (Cú pháp CŨ, nhưng bắt buộc)
#    (Các cài đặt này sẽ gây ra WARNINGS, nhưng cần thiết để dj-rest-auth hoạt động)
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False # Rất quan trọng

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
