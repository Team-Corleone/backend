"""
ASGI config for CineSocial project.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from apps.games import urls as game_urls

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CineSocial.settings.dev')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            game_urls.websocket_urlpatterns
        )
    ),
}) 