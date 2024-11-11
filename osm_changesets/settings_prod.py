import os
from pathlib import Path

from osm_changesets.settings import *  # noqa: F401, F403

ALLOWED_HOSTS = [os.environ["ALLOWED_HOST"]]
DEBUG = False
SECRET_KEY = (
    Path(os.environ.get("SECRET_KEY_FILE", "/run/keys/osm-changesets-secret-key"))
    .read_text()
    .strip()
)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "unix:///run/redis-osm-changesets/redis.sock",
    }
}

CELERY_BROKER = "redis+socket:///run/redis-osm-changesets/redis.sock"
CELERY_BACKEND = "redis+socket:///run/redis-osm-changesets/redis.sock"
