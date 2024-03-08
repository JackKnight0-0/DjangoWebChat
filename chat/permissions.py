from django.shortcuts import reverse, redirect
from allauth.account.models import EmailAddress
from django.contrib.auth.mixins import UserPassesTestMixin


class EmailIsVerified(UserPassesTestMixin):
    def test_func(self):
        if not EmailAddress.objects.get(user=self.request.user).verified:
            return False
        return True

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result:
            return redirect(reverse('profile'))
        return super().dispatch(request, *args, **kwargs)
