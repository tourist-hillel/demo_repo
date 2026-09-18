import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.group_room_name = f'chat_{self.room_name}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            print('No auth')
            await self.close()
            return

        await self.channel_layer.group_add(
            self.group_room_name,
            self.channel_name
        )

        await self.accept()

        await self.channel_layer.group_send(
            self.group_room_name,
            {
                'type': 'user_status',
                'message': f'{self.user} is connected...',
                'username': self.user.email or self.user.cell_phone,
                'status': 'online'
            }
        )

    async def disconnect(self, code: int) -> None:
        await self.channel_layer.group_send(
            self.group_room_name,
            {
                'type': 'user_status',
                'message': f'{self.user} is disconnect...',
                'username': self.user.email or self.user.cell_phone,
                'status': 'offline'
            }
        )
        await self.channel_layer.group_discard(
            self.group_room_name,
            self.channel_name
        )

    async def receive(self, text_data: str | None = None, bytes_data: bytes | None = None) -> None:
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')
        if not message:
            await self.send(text_data=json.dumps({
                'error': 'Invalid message'
            }))
        else:
            user = self.scope['user']
            await self.channel_layer.group_send(
                self.group_room_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': user.email or user.cell_phone
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'username': event['username'],
            'message': event['message']
        }))

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'status',
            'username': event['username'],
            'message': event['message'],
            'status': event['status']
        }))
