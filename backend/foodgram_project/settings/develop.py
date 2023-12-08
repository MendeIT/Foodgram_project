from django.conf import settings

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': settings.BASE_DIR / 'db.sqlite3',
    }
}

INTERNAL_IPS = ['127.0.0.1']

list_develop_settings = [
    'debug_toolbar',
    'django_extensions',
]

settings.INSTALLED_APPS.extend(list_develop_settings)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'custom': {
            'format': (
                '{asctime} - {levelname} - {module} '
                '- {funcName} - {lineno} - {message}'
            ),
            'style': '{',
        },
        'debug': {
            'format': (
                '[{levelname}] - {module} - {funcName} - {lineno} - {message}'
            ),
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'custom'
        },
        'console_simple': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'debug'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console_simple'],
            'level': 'WARNING',
        },
        'develop': {
            'handlers': ['console'],
            'level': 'DEBUG',
        }
    },
}
