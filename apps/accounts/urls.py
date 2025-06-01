"""
URLs pour l'application accounts (authentification et profils)
"""

from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # Authentification
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path(
        "register/artist/", views.ArtistRegisterView.as_view(), name="artist_register"
    ),
    path(
        "register/organizer/",
        views.OrganizerRegisterView.as_view(),
        name="organizer_register",
    ),
    # Vérification email
    path(
        "verify-email/<str:token>/",
        views.VerifyEmailView.as_view(),
        name="verify_email",
    ),
    path(
        "resend-verification/",
        views.ResendVerificationView.as_view(),
        name="resend_verification",
    ),
    # Profils
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/", views.EditProfileView.as_view(), name="edit_profile"),
    path(
        "profile/organizer/edit/",
        views.EditOrganizerProfileView.as_view(),
        name="edit_organizer_profile",
    ),
    # Mot de passe
    path(
        "password/change/", views.ChangePasswordView.as_view(), name="change_password"
    ),
    path("password/reset/", views.PasswordResetView.as_view(), name="password_reset"),
    path(
        "password/reset/confirm/<uidb64>/<token>/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]
