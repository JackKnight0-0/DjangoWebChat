from django import forms
from django.contrib.auth import get_user_model, forms as auth_forms

import allauth.account.forms as allauth_forms


class UpdateUsernameForm(forms.ModelForm):
    username = forms.CharField(required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))

    class Meta:
        model = get_user_model()
        fields = (
            'username',
        )


class UpdateEmailForm(forms.ModelForm):
    email = forms.EmailField(required=True,
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))

    class Meta:
        model = get_user_model()
        fields = (
            'email',
        )


class UpdateAvatarForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = (
            'avatar',
        )


class CustomLoginForm(allauth_forms.LoginForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['login'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Username or Email'})
        self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})


class CustomSignUpForm(allauth_forms.SignupForm):
    def __init__(self, *args, **kwargs):
        super(CustomSignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Username'})
        self.fields['email'].widget = forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
        self.fields['password1'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Password'})


class CustomChangePassword(allauth_forms.ChangePasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomChangePassword, self).__init__(*args, **kwargs)
        self.fields['oldpassword'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Old Password'})
        self.fields['password1'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'New Password'})
        self.fields['password2'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'New Password ( Again )'})


class CustomResetPasswordForm(auth_forms.PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(CustomResetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})


class CustomResetPasswordFromKeyForm(auth_forms.SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomResetPasswordFromKeyForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'New password'})
        self.fields['new_password2'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'New password ( again )'})
