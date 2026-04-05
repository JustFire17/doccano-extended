import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.shortcuts import get_object_or_404
from django.apps import apps

logger = logging.getLogger(__name__)

class DiscussionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.discussion_id = self.scope['url_route']['kwargs']['discussion_id']
        self.room_group_name = f'discussion_{self.project_id}_{self.discussion_id}'
        
        logger.info(f"WebSocket conectando: project_id={self.project_id}, discussion_id={self.discussion_id}")
        logger.info(f"User: {self.scope.get('user', 'Anonymous')}")

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"WebSocket conectado: {self.room_group_name}")
        
        # Enviar todas as mensagens existentes para o cliente que acabou de conectar
        messages = await self.get_all_messages()
        if messages:
            logger.info(f"Enviando {len(messages)} mensagens existentes para o novo cliente")
            for message in messages:
                await self.send(text_data=json.dumps({
                    'message': message
                }))
        else:
            logger.info("Nenhuma mensagem existente para enviar")

    async def disconnect(self, close_code):
        # Leave room group
        logger.info(f"WebSocket desconectando: {self.room_group_name}, code: {close_code}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            logger.info(f"Recebendo mensagem: {text_data}")
            text_data_json = json.loads(text_data)
            message_content = text_data_json['content']
            user = self.scope['user']
            
            logger.info(f"Mensagem de {user} para {self.room_group_name}: {message_content[:50]}...")

            # Save message to database
            message = await self.save_message(user, message_content)
            if not message:
                logger.error("Falha ao salvar mensagem no banco de dados")
                await self.send(text_data=json.dumps({
                    'error': 'Falha ao salvar mensagem'
                }))
                return
                
            serializer = await self.get_message_data(message)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': serializer
                }
            )
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def save_message(self, user, content):
        try:
            # Importação lazy para evitar problemas de inicialização
            Discussion = apps.get_model('projects', 'Discussion')
            DiscussionMessage = apps.get_model('projects', 'DiscussionMessage')
            
            discussion = get_object_or_404(Discussion, pk=self.discussion_id, project_id=self.project_id)
            if not user.is_authenticated:
                logger.error(f"Usuário não autenticado tentando enviar mensagem para discussion_id={self.discussion_id}")
                return None
                
            message = DiscussionMessage.objects.create(
                discussion=discussion,
                sender=user,
                content=content
            )
            logger.info(f"Mensagem salva com ID {message.id}")
            return message
        except Exception as e:
            logger.error(f"Erro ao salvar mensagem: {str(e)}")
            return None

    @database_sync_to_async
    def get_message_data(self, message):
        # Importação lazy para evitar problemas de inicialização
        from .serializers import DiscussionMessageSerializer
        serializer = DiscussionMessageSerializer(message)
        return serializer.data

    @database_sync_to_async
    def get_all_messages(self):
        try:
            # Importação lazy para evitar problemas de inicialização
            Discussion = apps.get_model('projects', 'Discussion')
            DiscussionMessage = apps.get_model('projects', 'DiscussionMessage')
            from .serializers import DiscussionMessageSerializer
            
            discussion = get_object_or_404(Discussion, pk=self.discussion_id, project_id=self.project_id)
            messages = DiscussionMessage.objects.filter(discussion=discussion).order_by('created_at')
            serializer = DiscussionMessageSerializer(messages, many=True)
            return serializer.data
        except Exception as e:
            logger.error(f"Erro ao obter mensagens existentes: {str(e)}")
            return [] 