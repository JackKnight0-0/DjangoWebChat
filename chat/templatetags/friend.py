from django import template

register = template.Library()


@register.simple_tag(name='get_friend')
def get_friend(user, chat):
    return chat.users.exclude(pk=user.pk)[0]

