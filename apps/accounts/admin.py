"""
Configuration de l'administration Django pour les comptes utilisateurs
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, ArtistProfile, OrganizerProfile, EmailVerificationToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Administration personnalisée pour le modèle User
    """

    list_display = (
        "email",
        "first_name",
        "last_name",
        "user_type",
        "is_active",
        "email_verified",
        "date_joined",
    )
    list_filter = (
        "user_type",
        "is_active",
        "email_verified",
        "is_staff",
        "date_joined",
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Informations personnelles"),
            {"fields": ("first_name", "last_name", "user_type")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "email_verified",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Dates importantes"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "user_type",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


@admin.register(ArtistProfile)
class ArtistProfileAdmin(admin.ModelAdmin):
    """
    Administration pour les profils d'artistes
    """

    list_display = (
        "get_display_name",
        "user_email",
        "city",
        "region",
        "is_available",
        "rating_average",
        "total_reviews",
        "profile_views",
    )
    list_filter = ("is_available", "city", "region", "created_at")
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "stage_name",
        "city",
    )
    readonly_fields = (
        "rating_average",
        "total_reviews",
        "profile_views",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            _("Informations de base"),
            {"fields": ("user", "stage_name", "phone_number", "whatsapp_number")},
        ),
        (
            _("Profil"),
            {"fields": ("bio", "profile_picture", "city", "region", "is_available")},
        ),
        (
            _("Statistiques"),
            {
                "fields": ("rating_average", "total_reviews", "profile_views"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Dates"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = _("Email")

    def get_display_name(self, obj):
        return obj.get_display_name()

    get_display_name.short_description = _("Nom d'affichage")


@admin.register(OrganizerProfile)
class OrganizerProfileAdmin(admin.ModelAdmin):
    """
    Administration pour les profils d'organisateurs
    """

    list_display = (
        "get_display_name",
        "user_email",
        "organization_type",
        "city",
        "region",
        "created_at",
    )
    list_filter = ("organization_type", "city", "region", "created_at")
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "organization_name",
        "city",
    )
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            _("Informations de base"),
            {"fields": ("user", "phone_number", "whatsapp_number")},
        ),
        (
            _("Organisation"),
            {"fields": ("organization_name", "organization_type", "city", "region")},
        ),
        (
            _("Dates"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = _("Email")

    def get_display_name(self, obj):
        return obj.get_display_name()

    get_display_name.short_description = _("Nom d'affichage")


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """
    Administration pour les tokens de vérification email
    """

    list_display = (
        "user_email",
        "token",
        "is_used",
        "is_expired_display",
        "created_at",
        "expires_at",
    )
    list_filter = ("is_used", "created_at", "expires_at")
    search_fields = ("user__email", "token")
    readonly_fields = ("token", "created_at")

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = _("Email utilisateur")

    def is_expired_display(self, obj):
        return obj.is_expired()

    is_expired_display.boolean = True
    is_expired_display.short_description = _("Expiré")
