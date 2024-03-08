from django.contrib.auth.tokens import PasswordResetTokenGenerator

from allauth.account.models import EmailAddress
from django.shortcuts import get_object_or_404


class EmailTokenGenerate(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        email = get_object_or_404(EmailAddress, user=user)

        return f"{user.pk}{timestamp}{email.email}{email.verified}"

email_token = EmailTokenGenerate()