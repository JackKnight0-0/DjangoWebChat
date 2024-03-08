from django.db import models
from django.contrib.auth.models import AbstractUser

from PIL import Image


class CustomUser(AbstractUser):

    status = models.OneToOneField(to='Status', on_delete=models.CASCADE, related_name='user')
    avatar = models.ImageField(upload_to='avatars/%Y/%m/%d', default='avatars/default_avatar.jpg')
    friend = models.ManyToManyField(to='self', related_name='friends', symmetrical=False)

    def save(self, *args, **kwargs):
        super(CustomUser, self).save(*args, **kwargs)
        avatar = Image.open(self.avatar.path)

        if avatar.height > 300 or avatar.width > 300:
            resize = (300, 300)
            avatar.thumbnail(resize)
            avatar.save(self.avatar.path)


class Status(models.Model):
    class ChooseStatus(models.TextChoices):
        offline = ('offline', 'Offline')
        online = ('online', 'Online')
        __empty__ = 'Status'

    status = models.CharField(choices=ChooseStatus, default=ChooseStatus.offline, editable=False)

    def __str__(self):
        return self.status

    class Meta:
        verbose_name = 'Status'
        verbose_name_plural = 'Status'
