from django.db.models.signals import pre_save
from django.dispatch.dispatcher import receiver
from django.contrib.auth import get_user_model

from accounts.models import Status


@receiver(pre_save, sender=get_user_model())
def create_status_for_user(sender, instance, *args, **kwargs):
    if instance.pk is None:
        status = Status.objects.create(status=Status.ChooseStatus.offline)
        instance.status = status
