from .base import *

DEBUG = True

INTERNAL_IPS = [
    "127.0.0.1",
]

MEDIA_ROOT = BASE_DIR.parent / 'media'
MEDIA_URL = '/media/'