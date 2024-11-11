from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = "django-insecure-9e%=k9cx$qqvm5k743e0nrmd#@v@&p9m+syq3-fx(2azkba3fg"

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost", ".local"]

INSTALLED_APPS = ["django.contrib.staticfiles", "osm_changesets"]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "osm_changesets.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(BASE_DIR / "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
            ],
        },
    },
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "unix:///run/user/1000/redis.sock",
    }
}

TIME_ZONE = "UTC"

USE_I18N = False

STATIC_URL = "static/"
STATIC_ROOT = str(BASE_DIR.parent / "public")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"level": "INFO", "class": "logging.StreamHandler"}},
    "loggers": {"csfd_export": {"level": "INFO", "handlers": ["console"]}},
}

CELERY_BROKER = "redis+socket:///run/user/1000/redis.sock"
CELERY_BACKEND = "redis+socket:///run/user/1000/redis.sock"
CELERY_RESULT_EXPIRES = timedelta(days=30)
