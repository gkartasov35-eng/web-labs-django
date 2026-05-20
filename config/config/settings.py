"""
Django settings for the web programming labs project.
Local mode uses SQLite and DEBUG=True. Hosting mode is controlled through
environment variables: DEBUG, SECRET_KEY, ALLOWED_HOSTS, DATABASE_URL.
"""

import os
from importlib.util import find_spec
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Для локального запуска есть учебный ключ, на хостинге задаётся SECRET_KEY.
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-dev-key-for-web-labs-only-change-on-hosting'
)

DEBUG = os.environ.get('DEBUG', '1').lower() in ('1', 'true', 'yes', 'on')

def env_list(name, default=''):
    return [item.strip() for item in os.environ.get(name, default).split(',') if item.strip()]

ALLOWED_HOSTS = env_list(
    'ALLOWED_HOSTS',
    '127.0.0.1,localhost,.onrender.com'
)
CSRF_TRUSTED_ORIGINS = env_list(
    'CSRF_TRUSTED_ORIGINS',
    'https://*.onrender.com'
)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
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

# WhiteNoise нужен только на хостинге для раздачи static-файлов через Django/Gunicorn.
if find_spec('whitenoise'):
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Если на хостинге подключить PostgreSQL и задать DATABASE_URL, проект сам переключится на него.
if os.environ.get('DATABASE_URL') and find_spec('dj_database_url'):
    import dj_database_url
    DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=not DEBUG)

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
if find_spec('whitenoise'):
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

LOGIN_URL = '/auth/'
LOGIN_REDIRECT_URL = '/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
