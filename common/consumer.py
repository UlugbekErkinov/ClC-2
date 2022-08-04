from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
import json


from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async

from chat.models import Notifications


class ChatConsumer(WebsocketConsumer):
    room_group_name = "clc"
    
    

    
    def connect(self):
        # self.room_name = self.scope['url_route']['kwargs']['room_name']
        # self.room_group_name = f'chat_{self.room_name}'
        # self.room = Room.objects.get(name=self.room_name)

        # connection has to be accepted
        self.accept()

        # join the room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )

    def receive(self, text_data=None, type='receive', bytes_data=None, ):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        print(message)
        print(text_data_json)


        if isinstance(text_data, dict):
            text_data_json = text_data
        else:
            text_data_json = json.loads(text_data)


        # send chat message event to the room
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
            }
        )

    def chat_message(self, event):
        self.send(text_data=json.dumps(event['data']))
    

    def chat_message_without_data(self, event):
        self.send(text_data=json.dumps(event))


        
    
    async def websocket_connect(self, event):
        print('connected', event)
        print('Am i finallyy here')
        print(self.scope['user'].id)
        await self.accept()


        await self.send(json.dumps({
            "type": "websocket.send",
                    "text": "hello world"
        }))
    
