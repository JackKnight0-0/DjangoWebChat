from django.contrib.auth.mixins import UserPassesTestMixin

from allauth.account.models import EmailAddress


class IsEmailAlreadyVerified(UserPassesTestMixin):
    def test_func(self):
        if EmailAddress.objects.get(user=self.request.user).verified:
            return True
        return True
