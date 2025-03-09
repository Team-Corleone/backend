from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# CORS ayarları
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Debug Toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
INTERNAL_IPS = ['127.0.0.1']

# Email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' 