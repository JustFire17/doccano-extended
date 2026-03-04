"""
ASGI config for doccano project.
It exposes the ASGI callable as a module-level variable named `application`.
"""

import os

import django
from django.core.asgi import get_asgi_application

# Configurar ambiente Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
django.setup()

from channels.auth import AuthMiddlewareStack  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from projects.middleware import TokenAuthMiddleware  # noqa: E402
from projects.routing import websocket_urlpatterns  # noqa: E402

# Aplicação ASGI
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": TokenAuthMiddleware(AuthMiddlewareStack(URLRouter(websocket_urlpatterns))),
    }
)
