"""
ASGI config for doccano project.
It exposes the ASGI callable as a module-level variable named `application`.
"""

import os
import django

# Configurar ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

# Importar componentes após inicialização do Django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from projects.middleware import TokenAuthMiddleware
from projects.routing import websocket_urlpatterns

# Aplicação ASGI
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TokenAuthMiddleware(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
}) 