from django.conf import settings

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': settings.BASE_DIR / 'db.sqlite3',
    }
}

INTERNAL_IPS = ['127.0.0.1']

settings.INSTALLED_APPS.append('debug_toolbar')


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "custom": {
            "format": (
                "{asctime} - {levelname} - {module} "
                "- {funcName} - {lineno} - {message}"
            ),
            "style": "{",
        },
        "debug": {
            "format": ("[{levelname}] - {module} "
                       "- {funcName} - {lineno} - {message}"),
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "debug"
        },
    },
    "loggers": {
        "root": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}
