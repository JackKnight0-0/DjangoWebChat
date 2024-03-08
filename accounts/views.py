from django.contrib.auth import get_user_model
from django.contrib.auth.views import INTERNAL_RESET_SESSION_TOKEN
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views import generic as django_generic
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import views as drf_generic
from django.shortcuts import redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.core.cache import cache
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import UserPassesTestMixin

from django.core.mail import EmailMessage
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.template.loader import render_to_string

from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework.response import Response

import accounts.forms as forms
from allauth.account.models import EmailAddress

from allauth.account import views as allauth_view
from .token_generate import email_token
from .permissions import IsEmailAlreadyVerified

from chat.models import ChatOnoToOne


class UserProfileView(LoginRequiredMixin, django_generic.FormView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = dict()
        context['username_form'] = forms.UpdateUsernameForm(instance=self.request.user)
        context['email_form'] = forms.UpdateEmailForm(instance=self.request.user)
        context['avatar_form'] = forms.UpdateAvatarForm()
        context['email_verified'] = EmailAddress.objects.get(user=self.request.user).verified
        return context

    def get_success_url(self):
        return redirect(reverse('profile'))

    def forms_valid(self, list_form):
        for form in list_form:
            form.save()

        return self.get_success_url()

    def change_email(self, email):
        user = self.request.user
        current_email = EmailAddress.objects.get(user=user)
        current_email.delete()
        EmailAddress.objects.create(user=user, email=email, primary=True)

    def check_forms(self):
        data = self.request.POST
        email_form = forms.UpdateEmailForm(self.request.POST, instance=self.request.user)
        username_form = forms.UpdateUsernameForm(self.request.POST, instance=self.request.user)
        avatar_form = forms.UpdateAvatarForm(self.request.POST, self.request.FILES, instance=self.request.user)
        context = self.get_context_data()
        changed_forms = []
        if 'email' in data:
            if not email_form.is_valid():
                context['email_form'] = email_form
                return self.render_to_response(context=context)
            self.change_email(email=email_form.cleaned_data.get('email'))
        if 'username' in data:
            if not username_form.is_valid():
                context['username_form'] = username_form
                return self.render_to_response(context=context)
            changed_forms.append(username_form)
        if avatar_form.is_valid():
            if not avatar_form.is_valid():
                context['avatar_form'] = avatar_form
                return self.render_to_response(context=context)
            changed_forms.append(avatar_form)
        return self.forms_valid(changed_forms)

    def post(self, request, *args, **kwargs):
        return self.check_forms()


class UserProfileDetailView(django_generic.DetailView):
    """
    Rendering userprofile detail and checking relationship with current user and owner of profile
    """
    model = get_user_model()
    template_name = 'accounts/profile_detail.html'

    def get_object(self, queryset=None):
        return get_object_or_404(get_user_model(), username=self.kwargs.get('username', None))

    def is_friend(self):
        return self.request.user in self.get_object().friends.all()

    def is_chat_exists(self):
        friend = self.get_object()
        self.chat = ChatOnoToOne.objects.filter(users__in=[friend, ]).filter(users__in=[self.request.user, ])
        return self.chat.exists()

    def get_chat(self):
        if self.is_chat_exists():
            return self.chat.first().uuid
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) or dict()
        context['userprofile'] = self.get_object()
        context['is_friend'] = self.is_friend()
        context['is_chat_exists'] = self.is_chat_exists()
        context['chat_uuid'] = self.get_chat()
        return context


class CustomLoginVIew(allauth_view.LoginView):
    form_class = forms.CustomLoginForm
    template_name = 'accounts/login.html'


class CustomSignUpView(allauth_view.SignupView):
    form_class = forms.CustomSignUpForm
    template_name = 'accounts/signup.html'


class CustomChangePasswordView(LoginRequiredMixin, allauth_view.PasswordChangeView):
    template_name = 'accounts/change_password.html'
    form_class = forms.CustomChangePassword

    def get_success_url(self):
        return reverse('home')


class CustomPasswordResetDoneView(UserPassesTestMixin, auth_views.PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'

    def test_func(self):
        path = str(get_current_site(request=self.request)) + reverse('account_password_reset')
        if self.request.META.get('HTTP_REFERER', False) and path in str(self.request.META.get('HTTP_REFERER')):
            return True
        return False

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result:
            raise Http404
        return super().dispatch(request, *args, **kwargs)


class CustomResetPasswordView(auth_views.PasswordResetView):
    template_name = 'registration/password_reset.html'
    form_class = forms.CustomResetPasswordForm
    success_url = reverse_lazy('account_password_reset_done')


class CustomResetPasswordFromKeyView(auth_views.PasswordResetConfirmView):
    template_name = 'registration/password_reset_from_key.html'
    form_class = forms.CustomResetPasswordFromKeyForm
    success_url = reverse_lazy('password_reset_complete')

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        if "uidb64" not in kwargs or "token" not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'uidb64' and 'token' parameters."
            )

        self.validlink = False
        self.user = self.get_user(kwargs["uidb64"])

        if self.user is not None:
            token = kwargs["token"]
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(
                        token, self.reset_url_token
                    )
                    return HttpResponseRedirect(redirect_url)

        # raise Error if token is not valid
        raise Http404


class CustomPasswordResetCompleteView(UserPassesTestMixin, auth_views.PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'

    def test_func(self):
        # check if user came from CustomResetPasswordFromKeyView
        if self.request.META.get('HTTP_REFERER', False) and '/set-password/' in str(
                self.request.META.get('HTTP_REFERER')):
            return True
        return False

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result:
            raise Http404
        return super().dispatch(request, *args, **kwargs)


class SendEmailView(LoginRequiredMixin, IsEmailAlreadyVerified, drf_generic.APIView):

    def send_confire_email(self):
        user = self.request.user
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_token.make_token(user=self.request.user)
        domain = get_current_site(request=self.request)
        subject = 'Verification email address ' + user.username
        body = render_to_string(template_name='accounts/email/verification_email.html', context={
            'uidb64': uidb64,
            'token': token,
            'domain': domain,
            'user': user
        })
        message = EmailMessage(subject=subject, body=body, to=[user.email, ])
        message.send()

    def post(self, request, *args, **kwargs):
        cache_value = f'email_post_{self.request.user.pk}'

        post_was_made = cache.get(cache_value, 0)

        if post_was_made:
            return Response({'status': 'Wait'})

        cache.set(cache_value, 1, 60 * 3)

        self.send_confire_email()

        return Response({'status': 'Success'})


class EmailFromKeyDoneView(LoginRequiredMixin, IsEmailAlreadyVerified, django_generic.TemplateView):
    template_name = 'accounts/email_from_key_done.html'


class CheckEmailVerifView(LoginRequiredMixin, IsEmailAlreadyVerified, django_generic.View):

    def get_success_url(self):
        return redirect(reverse('email_from_key_done'))

    def get(self, request, *args, **kwargs):

        try:
            uidb64 = force_str(urlsafe_base64_decode(self.kwargs.get('uidb64')))
            token = self.kwargs.get('token')
            user = None
            user = get_user_model().objects.get(pk=uidb64)
        except (get_user_model().DoesNotExist, ValueError, OverflowError, SyntaxError):
            raise Http404

        if user is not None and email_token.check_token(user=user, token=token):
            email = get_object_or_404(EmailAddress, user=user)
            email.verified = True
            email.save()
            return self.get_success_url()

        raise Http404
