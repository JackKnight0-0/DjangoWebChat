from django.contrib import admin

from .models import ChatOnoToOne, Message


@admin.register(ChatOnoToOne)
class ChatOnoToOneAdmin(admin.ModelAdmin):
    exclude = ['uuid', ]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    exclude = ['update_at', ]
    actions = ['set_unread', ]

    @admin.action(description='set unread')
    def set_unread(self, request, query):
        query.update(is_read=False)
