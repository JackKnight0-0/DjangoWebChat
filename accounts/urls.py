from django.urls import path, re_path

from django.contrib.auth import views as django_views

from allauth.account.urls import views as allauth_views

import accounts.views as views

urlpatterns = [
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/<slug:username>/', views.UserProfileDetailView.as_view(), name='profile_detail'),
    path('logout/', allauth_views.LogoutView.as_view(), name='account_logout'),
    path('login/', views.CustomLoginVIew.as_view(), name='account_login'),
    path('signup/', views.CustomSignUpView.as_view(), name='account_signup'),
    # emails
    path("email/", allauth_views.email, name="account_email"),
    path(
        "confirm-email/",
        allauth_views.email_verification_sent,
        name="account_email_verification_sent",
    ),
    re_path(
        r"^confirm-email/(?P<key>[-:\w]+)/$",
        allauth_views.confirm_email,
        name="account_confirm_email",
    ),
    path('email/verified/', views.SendEmailView.as_view(), name='send_email_from_key'),
    path('email/key/done/', views.EmailFromKeyDoneView.as_view(), name='email_from_key_done'),
    path('email/<uidb64>/<token>/', views.CheckEmailVerifView.as_view(), name='email_verif'),
    # password
    path('password/change/', views.CustomChangePasswordView.as_view(), name='account_change_password_done'),
    path("password/reset/", views.CustomResetPasswordView.as_view(), name="account_password_reset"),
    path(
        "password/reset/done/",
        views.CustomPasswordResetDoneView.as_view(),
        name="account_password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        views.CustomResetPasswordFromKeyView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        views.CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
