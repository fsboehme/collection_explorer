from .base import *

DEBUG = False
TEMPLATE_DEBUG = False

SITE_NAME = 'Collection Explorer'
SITE_DOMAIN = 'collection-explorer.travelix.earth'

ALLOWED_HOSTS += [f'.{SITE_DOMAIN}']
WSGI_APPLICATION = 'django_project.wsgi.prod.application'