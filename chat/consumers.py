import json

from channels.generic.websocket import AsyncWebsocketConsumer

from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from django.http import Http404
from django.shortcuts import aget_object_or_404

from accounts.models import Status

from .models import ChatOnoToOne, Message
from .utils import ConsumerStatusMixin


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer for one-on-one chat, checks if the user is in the chat room and online,
    and if not, sends the message out of bounds
    and mark it as unread, save the message after sending it.
    """
    users = []

    def get_user_model(self):
        return self.scope['user']

    async def get_chat(self):
        """
        Checking if chat exists and if user in this chat, accepting connection otherwise closing
        """
        user = self.get_user_model()
        uuid_chat = self.scope['url_route']['kwargs']['uuid']
        chat = await aget_object_or_404(ChatOnoToOne, uuid=uuid_chat)
        if sync_to_async(chat.users.filter(pk=user.pk).exists)():
            if user not in self.users:
                self.users.append(user)
            await self.accept()
            return chat
        else:
            await self.close()

    def get_from_user(self):
        return self.scope['user'].username

    async def get_friend_user(self):
        chat = self.chat
        return await sync_to_async(chat.users.exclude(pk=self.get_user_model().pk).first)()

    async def send_message_outside_chat(self, event):
        """
        Checking if friend in chat and if not, sending a message outside the chat
        """
        friend = await self.get_friend_user()
        if len(self.users) < 2:
            channel_layer = get_channel_layer()
            await channel_layer.group_send(f"on_new_message_{friend.pk}",
                                           {'type': 'handle.message', 'from_user': event['from_user'],
                                            'message': event['message']})

    async def save_message(self, message):
        obj = await Message.objects.acreate(
            message=message,
            from_user=self.get_user_model(),
            chat=self.chat
        )
        return obj

    async def change_status(self, action):
        status = None
        user = self.get_user_model()
        status_user = await Status.objects.aget(user=user)

        if action == 'connected':
            status = Status.ChooseStatus.online

        elif action == 'disconnected':
            status = Status.ChooseStatus.offline

        status_user.status = status
        await status_user.asave()

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'status.changed',
                'status': status,
                'user': user
            }
        )

    async def the_message_is_read(self, message):
        if len(self.users) < 2:
            message.is_read = False
        else:
            message.is_read = True
        await message.asave()

    async def connect(self):
        self.chat = await self.get_chat()

        self.group_name = self.chat.name_chat()

        await self.channel_layer.group_add(self.group_name, channel=self.channel_name)

        await self.change_status('connected')

    async def receive(self, text_data=None, bytes_data=None):
        """
        Receiving a message and sending to send_message handler
        """
        text = json.loads(text_data)

        message = await self.save_message(message=text)

        await self.the_message_is_read(message=message)

        await self.channel_layer.group_send(self.group_name, {
            'type': 'send.message',
            "from_user": self.get_from_user(),
            'message': text
        })

    async def send_message(self, event):
        message = event['message']
        from_user = event['from_user']

        if from_user == self.get_user_model().username:
            from_user = 'me'

        ready_message = {'type': 'text', 'from_user': from_user, 'message': message}

        await self.send_message_outside_chat(event=event)

        await self.send(json.dumps(ready_message))

    async def status_changed(self, event):
        """
        If a user leaves the chat, changing status
        """
        status = event['status']
        user = event['user']
        if user != self.get_user_model():
            await self.send(text_data=json.dumps({
                'type': 'user.status',
                'status': status
            }))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        self.users.remove(self.get_user_model())
        await self.change_status('disconnected')


class GlobalConsumer(ConsumerStatusMixin, AsyncWebsocketConsumer):
    """
    Consumer for changing status user if user still in website
    """

    async def connect(self):
        self.user = self.scope['user']
        self.group_name = f'on_new_message_{self.user.pk}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.change_status(user=self.user, action='connected')

    async def disconnect(self, code):
        await self.close()
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.change_status(user=self.user, action='disconnected')


class ChatListConsumer(ConsumerStatusMixin, AsyncWebsocketConsumer):
    """
    Consumer to handle messages which outside the users chat
    """

    async def connect(self):
        self.user = self.scope['user']
        self.group_name = f'on_new_message_{self.user.pk}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.change_status(user=self.user, action='connected')

    async def disconnect(self, code):
        await self.close()
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.change_status(user=self.user, action='disconnected')

    async def handle_message(self, data):
        message = data['message']
        from_user = data['from_user']
        await self.send(json.dumps({'type': 'new.update', 'from_user': from_user, 'message': message}))
