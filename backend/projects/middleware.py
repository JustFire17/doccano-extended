from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
import logging
import json

logger = logging.getLogger(__name__)

@database_sync_to_async
def get_user_from_session(session_id):
    from django.contrib.sessions.models import Session
    try:
        # Tentar obter a sessão pelo ID
        session = Session.objects.get(session_key=session_id)
        session_data = session.get_decoded()
        uid = session_data.get('_auth_user_id')
        
        # Se encontrou o ID do usuário na sessão
        if uid:
            User = get_user_model()
            return User.objects.get(id=uid)
        return AnonymousUser()
    except Exception as e:
        logger.warning(f"Erro ao obter usuário da sessão: {str(e)}")
        return AnonymousUser()

@database_sync_to_async
def get_user_from_token(token_key):
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()

class TokenAuthMiddleware:
    """
    Custom auth middleware for Channels que suporta autenticação de sessão e token
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Verificar se é um tipo de scope de websocket
        if scope["type"] != "websocket":
            return await self.app(scope, receive, send)

        # Extrair parâmetros da query string
        query_params = parse_qs(scope["query_string"].decode())
        headers = dict(scope['headers'])
        
        user = AnonymousUser()
        
        # Tentar autenticar por token
        token_key = None
        if b'token' in query_params:
            token_key = query_params[b'token'][0].decode()
            
        if token_key:
            user = await get_user_from_token(token_key)
            if not user.is_anonymous:
                logger.info(f"WebSocket autenticado via token para o usuário: {user.username}")
                scope["user"] = user
                return await self.app(scope, receive, send)
        
        # Tentar autenticar por cookie de sessão
        cookie_header = headers.get(b'cookie', b'').decode()
        cookies = {}
        
        # Processar cookies
        for item in cookie_header.split(';'):
            if not item.strip():
                continue
            if '=' in item:
                name, value = item.strip().split('=', 1)
                cookies[name] = value
        
        # Procurar o cookie de sessão do Django
        session_id = cookies.get('sessionid')
        
        if session_id:
            logger.debug(f"Tentando autenticar por cookie de sessão: {session_id}")
            user = await get_user_from_session(session_id)
            if not user.is_anonymous:
                logger.info(f"WebSocket autenticado via sessão para o usuário: {user.username}")
                scope["user"] = user
                return await self.app(scope, receive, send)
        
        # Se nenhuma autenticação funcionou
        logger.warning("WebSocket sem autenticação válida")
        scope["user"] = AnonymousUser()
        return await self.app(scope, receive, send) 