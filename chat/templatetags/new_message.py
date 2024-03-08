from django import template
from django.db.models import Q
from django.conf import settings

from chat.models import Message
import datetime

register = template.Library()


@register.simple_tag(name='get_new_message_count')
def get_new_message_count(chat, user):
    return len(
        Message.objects.filter(Q(chat=chat) & Q(is_read=False)).exclude(
            from_user=user)[:99])


@register.simple_tag(name='get_format_date')
def get_format_date(date):
    if date:
        if (datetime.datetime.now().replace(tzinfo=None) - date.replace(tzinfo=None)).days < 1:
            return f'{str(date.hour).zfill(2)}:{str(date.minute).zfill(2)}'
        else:
            return date.strftime('%d.%m.%Y')
    return None
