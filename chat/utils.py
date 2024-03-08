from accounts.models import Status


class ConsumerStatusMixin(object):
    """
    Mixin for change user status after connection or disconnect
    """
    async def change_status(self, user, action):
        status = await Status.objects.aget(user=user)
        if action == 'connected':
            status.status = Status.ChooseStatus.online

        elif action == 'disconnected':
            status.status = Status.ChooseStatus.offline
        status = await status.asave()
        return status
