"""
Django settings for bonart_auction project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from django.contrib.messages import constants as message_constants

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-vo+in*a%928*&=h256-)idrg22e36c@*l0@$y#i18agh8#e4(a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

MESSAGE_TAGS = {
    message_constants.DEBUG: 'secondary',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'danger',
}
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-email-password'
DEFAULT_FROM_EMAIL = 'BonArt Auction <no-reply@bonartauction.com>'

LOGIN_URL = 'login'  # Имя маршрута для входа
LOGIN_REDIRECT_URL = 'home'  # Маршрут после успешного входа
LOGOUT_REDIRECT_URL = 'home'  # Маршрут после выхода

INSTALLED_APPS = [
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'auctions.apps.AuctionsConfig',
]


CELERY_BROKER_URL = 'redis://localhost:6379/0'  # URL вашего брокера (Redis)
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # Backend для хранения результатов
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'  # Установите вашу временную зону

# Настройка периодических задач через Celery Beat
CELERY_BEAT_SCHEDULE = {
    'close-expired-auctions-every-minute': {
        'task': 'auctions.tasks.close_expired_auctions',
        'schedule': 60.0,  # Каждую минуту
    },
}

CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        '__main__': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}


# settings.py
TELEGRAM_BOT_TOKEN = '7328241609:AAEykAshzlBpX0CGIkAGcVDLTHtAM_R0Bu8'

TWILIO_ACCOUNT_SID = 'ACc2700ae53baab5f2f158a38c4a3f0f8d'  # Получите из Twilio Console
TWILIO_AUTH_TOKEN = 'acce47bf6161a5dff057ff79456ee45d'   # Получите из Twilio Console
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'  # Номер из Sandbox

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'auctions.middleware.AutoLogoutMiddleware',
]

ROOT_URLCONF = 'bonart_auction.urls'

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

WSGI_APPLICATION = 'bonart_auction.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bonart_db',
        'USER': 'postgres',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
AUTH_USER_MODEL = 'auctions.CustomUser'

# Устанавливает время жизни сессии в секундах (например, 5 минут = 300 секунд)
SESSION_COOKIE_AGE = 300

# Указывает, чтобы сессия истекала, если пользователь закрыл браузер
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Asia/Almaty'  # Часовой пояс для Казахстана
USE_TZ = True  # Обязательно оставить включённым


LOGOUT_REDIRECT_URL = '/'  # Перенаправление на главную страницу после выхода

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
