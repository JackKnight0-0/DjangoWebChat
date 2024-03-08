from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Message


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            'pk',
            'username',
            'avatar'
        )


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = (
            'pk',
            'from_user',
            'message',
        )

    def to_representation(self, instance):
        """
        If a user owner of a message changing it for rendering in js, change a status message to read
        """
        response = super().to_representation(instance=instance)
        user = self.context.get('user')
        from_user = instance.from_user.username
        if from_user == user.username:
            from_user = 'me'
        response['from_user'] = from_user
        instance.is_read = True
        instance.save()
        return response
