"""
Django settings for config project.
"""
from pathlib import Path
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# 加载 .env 文件（优先加载项目根目录的 .env）
ENV_PATH = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=ENV_PATH)


# ===== Django 基础配置 =====

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-dev-key-change-in-production')
DEBUG = os.getenv('DJANGO_DEBUG', 'true').lower() in ('true', '1', 'yes')
ALLOWED_HOSTS = [
    h.strip() for h in os.getenv('DJANGO_ALLOWED_HOSTS', '*').split(',')
]


# ===== 应用配置 =====

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
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

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'


# ===== 数据库配置 =====

DB_ENGINE = os.getenv('DB_ENGINE', 'core.db_backend')
DB_NAME = os.getenv('DB_NAME', 'classmates_record')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_CONN_MAX_AGE = int(os.getenv('DB_CONN_MAX_AGE', '0'))

DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'CONN_MAX_AGE': DB_CONN_MAX_AGE,
    }
}


# ===== 自定义用户模型 =====

AUTH_USER_MODEL = 'core.User'

AUTHENTICATION_BACKENDS = [
    'core.backends.EmailAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]


# ===== 登录 / 登出 =====

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'


# ===== 密码验证 =====

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
]


# ===== 国际化 =====

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True


# ===== 静态与媒体文件 =====

STATIC_URL = os.getenv('STATIC_URL', '/static/')
STATICFILES_DIRS = [BASE_DIR / 'core' / 'static']

MEDIA_URL = os.getenv('MEDIA_URL', '/uploads/')
MEDIA_ROOT = BASE_DIR / 'core' / 'static' / 'core' / 'uploads'


# ===== 邮箱配置 =====

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.qq.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '465'))
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'true').lower() in ('true', '1', 'yes')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)


# ===== 会话配置 =====

SESSION_COOKIE_AGE = int(os.getenv('SESSION_COOKIE_AGE', str(7 * 24 * 60 * 60)))


# ===== 其他 =====

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ===== 生产环境安全配置 =====
# 当 DEBUG=False 时自动启用 HTTPS 相关安全设置
if not DEBUG:
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'true').lower() in ('true', '1', 'yes')
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'true').lower() in ('true', '1', 'yes')
    CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'true').lower() in ('true', '1', 'yes')
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    # HSTS 配置（建议生产环境开启，浏览器将强制使用 HTTPS）
    # SECURE_HSTS_SECONDS = 31536000  # 1年
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_PRELOAD = True
