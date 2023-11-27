import os

import sentry_sdk
from dotenv import load_dotenv
from sentry_sdk.integrations.django import DjangoIntegration

load_dotenv()

CSRF_TRUSTED_ORIGINS = (os.getenv(
    'CSRF_TRUSTED_ORIGINS', 'http://your_domain_name.django'
)).split()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'mydb'),
        'USER': os.getenv('POSTGRES_USER', 'myuser'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'mypass'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', 5432),
    }
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PAGINATION_CLASS': [
        'api.pagination.CustomPaginator',
    ],
    'PAGE_SIZE': 6,
    'SEARCH_PARAM': 'name',
}

sentry_sdk.init(
    dsn=('https://cf824c317dfa948ab6e82843a6b8304f@o4505985247150080.'
         + 'ingest.sentry.io/4506231236198400'),
    integrations=[DjangoIntegration(), ],
    traces_sample_rate=1.0,
    send_default_pii=True
)
