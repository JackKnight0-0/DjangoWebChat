from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import reverse

import uuid


class ChatOnoToOne(models.Model):
    uuid = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    users = models.ManyToManyField(to=get_user_model(), related_name='chats')

    def __str__(self):
        return self.uuid.__str__()

    def get_absolute_url(self):
        return reverse('chat_detail', kwargs={'uuid': self.uuid})

    def name_chat(self):
        return self.uuid.__str__()


class Message(models.Model):
    from_user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, related_name='messages')
    chat = models.ForeignKey(to='ChatOnoToOne', on_delete=models.CASCADE, related_name='messages')
    is_read = models.BooleanField(default=0)
    message = models.TextField(max_length=5000)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.message[:50]

    class Meta:
        ordering = ['-create_at']
