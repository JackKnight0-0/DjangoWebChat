from django.urls import re_path, path
from .consumers import ChatConsumer, GlobalConsumer, ChatListConsumer

websocket_urlpatterns = [
    path('chat/<uuid:uuid>/', ChatConsumer.as_asgi()),  # chat websocket
    path('', ChatListConsumer.as_asgi()),  # chat websocket for a list of chat page
    re_path('^(.*)$', GlobalConsumer.as_asgi()) # global websocket for any page in website
]
