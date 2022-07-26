import os
import sys

from .base import *
import dj_database_url

DEBUG = os.getenv("DEBUG", "False") == "True"
DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "False") == "True"
TEMPLATE_DEBUG = DEBUG

SITE_NAME = 'Collection Explorer'
SITE_DOMAIN = 'collection-explorer.travelix.earth'

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

WSGI_APPLICATION = 'django_project.wsgi.prod.application'

from django.core.management.utils import get_random_secret_key
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key())

if DEVELOPMENT_MODE is True:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
elif len(sys.argv) > 0 and sys.argv[1] != 'collectstatic':
    if os.getenv("DATABASE_URL", None) is None:
        raise Exception("DATABASE_URL environment variable not defined")
    DATABASES = {
        "default": dj_database_url.parse(os.environ.get("DATABASE_URL")),
    }

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")