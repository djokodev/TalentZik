"""
Vues pour l'authentification et les profils utilisateurs
"""

import secrets
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, UpdateView
from django.contrib.auth.views import (
    LoginView as BaseLoginView,
    LogoutView as BaseLogoutView,
)
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse

from .models import User, ArtistProfile, OrganizerProfile, EmailVerificationToken
from .forms import (
    TalentZikLoginForm,
    UserRegistrationForm,
    ArtistRegistrationForm,
    OrganizerRegistrationForm,
    ArtistProfileForm,
    OrganizerProfileForm,
    EditProfileForm,
)


class LoginView(BaseLoginView):
    """Vue de connexion"""

    form_class = TalentZikLoginForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        """Redirection après connexion réussie"""
        if self.request.user.is_artist:
            return reverse_lazy("accounts:profile")
        elif self.request.user.is_organizer:
            return reverse_lazy("accounts:profile")
        return reverse_lazy("home")

    def form_valid(self, form):
        """Actions après connexion réussie"""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Bienvenue {self.request.user.get_full_name()} ! Vous êtes maintenant connecté.",
        )
        return response


class LogoutView(BaseLogoutView):
    """Vue de déconnexion"""

    next_page = reverse_lazy("home")

    def dispatch(self, request, *args, **kwargs):
        """Actions avant déconnexion"""
        if request.user.is_authenticated:
            messages.info(request, "Vous avez été déconnecté avec succès.")
        return super().dispatch(request, *args, **kwargs)


class RegisterView(TemplateView):
    """Vue de choix du type d'inscription"""

    template_name = "accounts/register.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Choisissez votre profil",
                "page_description": "Rejoignez TalentZik en tant qu'artiste ou organisateur d'événements",
            }
        )
        return context


class ArtistRegisterView(CreateView):
    """Vue d'inscription pour les artistes"""

    form_class = ArtistRegistrationForm
    template_name = "accounts/artist_register.html"
    success_url = reverse_lazy("accounts:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Inscription Artiste",
                "page_description": "Créez votre profil d'artiste musical sur TalentZik",
            }
        )
        return context

    def form_valid(self, form):
        """Actions après inscription réussie"""
        response = super().form_valid(form)
        user = form.instance

        # Créer un token de vérification email
        self.create_email_verification_token(user)

        messages.success(
            self.request,
            f"Bienvenue {user.get_full_name()} ! Votre compte artiste a été créé avec succès. "
            f"Un email de vérification a été envoyé à {user.email}.",
        )

        # Connecter automatiquement l'utilisateur
        login(self.request, user)

        return response

    def create_email_verification_token(self, user):
        """Crée et envoie un token de vérification email"""
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=24)

        verification_token = EmailVerificationToken.objects.create(
            user=user, token=token, expires_at=expires_at
        )

        # Envoyer l'email de vérification
        self.send_verification_email(user, token)

        return verification_token

    def send_verification_email(self, user, token):
        """Envoie l'email de vérification"""
        verification_url = self.request.build_absolute_uri(
            f"/accounts/verify-email/{token}/"
        )

        subject = "Vérifiez votre adresse email - TalentZik"
        message = f"""
        Bonjour {user.get_full_name()},

        Bienvenue sur TalentZik ! Pour activer votre compte, veuillez cliquer sur le lien ci-dessous :

        {verification_url}

        Ce lien expirera dans 24 heures.

        Si vous n'avez pas créé de compte sur TalentZik, vous pouvez ignorer cet email.

        Cordialement,
        L'équipe TalentZik
        """

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Erreur envoi email: {e}")  # En développement


class OrganizerRegisterView(CreateView):
    """Vue d'inscription pour les organisateurs"""

    form_class = OrganizerRegistrationForm
    template_name = "accounts/organizer_register.html"
    success_url = reverse_lazy("accounts:profile")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Inscription Organisateur",
                "page_description": "Créez votre profil d'organisateur d'événements sur TalentZik",
            }
        )
        return context

    def form_valid(self, form):
        """Actions après inscription réussie"""
        response = super().form_valid(form)
        user = form.instance

        # Créer un token de vérification email
        self.create_email_verification_token(user)

        messages.success(
            self.request,
            f"Bienvenue {user.get_full_name()} ! Votre compte organisateur a été créé avec succès. "
            f"Un email de vérification a été envoyé à {user.email}.",
        )

        # Connecter automatiquement l'utilisateur
        login(self.request, user)

        return response

    def create_email_verification_token(self, user):
        """Crée et envoie un token de vérification email"""
        try:
            token = secrets.token_urlsafe(32)
            expires_at = timezone.now() + timedelta(hours=24)

            verification_token = EmailVerificationToken.objects.create(
                user=user, token=token, expires_at=expires_at
            )

            # Envoyer l'email de vérification
            self.send_verification_email(user, token)

            return verification_token
        except Exception as e:
            # Ne pas faire échouer l'inscription pour un problème d'email
            return None

    def send_verification_email(self, user, token):
        """Envoie l'email de vérification"""
        try:
            verification_url = self.request.build_absolute_uri(
                f"/accounts/verify-email/{token}/"
            )

            subject = "Vérifiez votre adresse email - TalentZik"
            message = f"""
            Bonjour {user.get_full_name()},

            Bienvenue sur TalentZik ! Pour activer votre compte, veuillez cliquer sur le lien ci-dessous :

            {verification_url}

            Ce lien expirera dans 24 heures.

            Si vous n'avez pas créé de compte sur TalentZik, vous pouvez ignorer cet email.

            Cordialement,
            L'équipe TalentZik
            """

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
        except Exception as e:
            pass  # Ne pas faire échouer l'inscription pour un problème d'email


class VerifyEmailView(TemplateView):
    """Vue de vérification d'email"""

    template_name = "accounts/verify_email.html"

    def get(self, request, token):
        """Traite la vérification d'email"""
        try:
            verification_token = get_object_or_404(
                EmailVerificationToken, token=token, is_used=False
            )

            if verification_token.is_expired():
                messages.error(
                    request,
                    "Ce lien de vérification a expiré. Demandez un nouveau lien.",
                )
                return redirect("accounts:resend_verification")

            # Marquer l'email comme vérifié
            user = verification_token.user
            user.email_verified = True
            user.save()

            # Marquer le token comme utilisé
            verification_token.is_used = True
            verification_token.save()

            messages.success(
                request,
                "Votre adresse email a été vérifiée avec succès ! Votre compte est maintenant activé.",
            )

            return redirect("accounts:profile")

        except EmailVerificationToken.DoesNotExist:
            messages.error(
                request, "Lien de vérification invalide. Demandez un nouveau lien."
            )
            return redirect("accounts:resend_verification")


class ResendVerificationView(LoginRequiredMixin, TemplateView):
    """Vue de renvoi de vérification"""

    template_name = "accounts/resend_verification.html"

    def post(self, request):
        """Renvoie un email de vérification"""
        user = request.user

        if user.email_verified:
            messages.info(request, "Votre email est déjà vérifié.")
            return redirect("accounts:profile")

        # Supprimer les anciens tokens non utilisés
        EmailVerificationToken.objects.filter(user=user, is_used=False).delete()

        # Créer un nouveau token
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=24)

        EmailVerificationToken.objects.create(
            user=user, token=token, expires_at=expires_at
        )

        # Envoyer l'email
        self.send_verification_email(user, token)

        messages.success(
            request, "Un nouvel email de vérification a été envoyé à votre adresse."
        )

        return redirect("accounts:profile")

    def send_verification_email(self, user, token):
        """Envoie l'email de vérification"""
        verification_url = self.request.build_absolute_uri(
            f"/accounts/verify-email/{token}/"
        )

        subject = "Vérifiez votre adresse email - TalentZik"
        message = f"""
        Bonjour {user.get_full_name()},

        Voici votre nouveau lien de vérification :

        {verification_url}

        Ce lien expirera dans 24 heures.

        Cordialement,
        L'équipe TalentZik
        """

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Erreur envoi email: {e}")


class ProfileView(LoginRequiredMixin, TemplateView):
    """Vue du profil utilisateur"""

    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context.update(
            {
                "user": user,
                "profile": self.get_user_profile(user),
                "page_title": f"Profil de {user.get_full_name()}",
            }
        )

        return context

    def get_user_profile(self, user):
        """Récupère le profil spécifique de l'utilisateur"""
        if user.is_artist:
            try:
                return user.artist_profile
            except ArtistProfile.DoesNotExist:
                return None
        elif user.is_organizer:
            try:
                return user.organizer_profile
            except OrganizerProfile.DoesNotExist:
                return None
        return None


class EditProfileView(LoginRequiredMixin, TemplateView):
    """Vue d'édition du profil avec formulaire complet"""

    template_name = "accounts/edit_profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Initialiser le formulaire avec les données utilisateur
        form = EditProfileForm(user=self.request.user)

        context.update(
            {
                "form": form,
                "page_title": "Éditer mon profil",
                "user_type": self.request.user.user_type,
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        """Traitement du formulaire"""
        form = EditProfileForm(request.POST, request.FILES, user=request.user)

        if form.is_valid():
            try:
                form.save(request.user)
                messages.success(request, "Votre profil a été mis à jour avec succès.")
                return redirect("accounts:profile")
            except Exception as e:
                messages.error(request, f"Erreur lors de la sauvegarde : {e}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

        # En cas d'erreur, retourner le formulaire avec les erreurs
        context = self.get_context_data()
        context["form"] = form
        return self.render_to_response(context)


class ChangePasswordView(TemplateView):
    """Vue de changement de mot de passe"""

    template_name = "accounts/change_password.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Changer mon mot de passe",
            }
        )
        return context


class PasswordResetView(TemplateView):
    """Vue de réinitialisation de mot de passe"""

    template_name = "accounts/password_reset.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Réinitialiser mon mot de passe",
            }
        )
        return context


class PasswordResetConfirmView(TemplateView):
    """Vue de confirmation de réinitialisation"""

    template_name = "accounts/password_reset_confirm.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Confirmer le nouveau mot de passe",
            }
        )
        return context
