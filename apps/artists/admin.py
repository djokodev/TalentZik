"""
Configuration de l'administration Django pour les données de référence musicales
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    MusicGenre,
    ArtistRole,
    Instrument,
    ArtistGenre,
    ArtistRoleAssignment,
    ArtistInstrument,
    ProfileView,
    WhatsAppClick,
    SearchQuery,
)


@admin.register(MusicGenre)
class MusicGenreAdmin(admin.ModelAdmin):
    """
    Administration pour les genres musicaux
    """

    list_display = ("name", "slug", "is_traditional", "is_active", "created_at")
    list_filter = ("is_traditional", "is_active", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at",)


@admin.register(ArtistRole)
class ArtistRoleAdmin(admin.ModelAdmin):
    """
    Administration pour les rôles d'artistes
    """

    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at",)


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    """
    Administration pour les instruments
    """

    list_display = ("name", "slug", "category", "is_active", "created_at")
    list_filter = ("category", "is_active", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at",)


@admin.register(ArtistGenre)
class ArtistGenreAdmin(admin.ModelAdmin):
    """
    Administration pour les relations artiste-genre
    """

    list_display = ("artist_name", "genre_name", "created_at")
    list_filter = ("genre", "created_at")
    search_fields = ("artist__user__email", "artist__stage_name", "genre__name")
    readonly_fields = ("created_at",)

    def artist_name(self, obj):
        return obj.artist.get_display_name()

    artist_name.short_description = _("Artiste")

    def genre_name(self, obj):
        return obj.genre.name

    genre_name.short_description = _("Genre")


@admin.register(ArtistRoleAssignment)
class ArtistRoleAssignmentAdmin(admin.ModelAdmin):
    """
    Administration pour les relations artiste-rôle
    """

    list_display = ("artist_name", "role_name", "created_at")
    list_filter = ("role", "created_at")
    search_fields = ("artist__user__email", "artist__stage_name", "role__name")
    readonly_fields = ("created_at",)

    def artist_name(self, obj):
        return obj.artist.get_display_name()

    artist_name.short_description = _("Artiste")

    def role_name(self, obj):
        return obj.role.name

    role_name.short_description = _("Rôle")


@admin.register(ArtistInstrument)
class ArtistInstrumentAdmin(admin.ModelAdmin):
    """
    Administration pour les relations artiste-instrument
    """

    list_display = ("artist_name", "instrument_name", "proficiency_level", "created_at")
    list_filter = ("instrument", "proficiency_level", "created_at")
    search_fields = ("artist__user__email", "artist__stage_name", "instrument__name")
    readonly_fields = ("created_at",)

    def artist_name(self, obj):
        return obj.artist.get_display_name()

    artist_name.short_description = _("Artiste")

    def instrument_name(self, obj):
        return obj.instrument.name

    instrument_name.short_description = _("Instrument")


@admin.register(ProfileView)
class ProfileViewAdmin(admin.ModelAdmin):
    """
    Administration pour les vues de profils
    """

    list_display = ("artist_name", "viewer_name", "viewer_ip", "viewed_at")
    list_filter = ("viewed_at",)
    search_fields = (
        "artist__user__email",
        "artist__stage_name",
        "viewer__email",
        "viewer_ip",
    )
    readonly_fields = ("viewed_at",)

    def artist_name(self, obj):
        return obj.artist.get_display_name()

    artist_name.short_description = _("Artiste")

    def viewer_name(self, obj):
        return obj.viewer.get_full_name() if obj.viewer else "Anonyme"

    viewer_name.short_description = _("Visiteur")


@admin.register(WhatsAppClick)
class WhatsAppClickAdmin(admin.ModelAdmin):
    """
    Administration pour les clics WhatsApp
    """

    list_display = ("artist_name", "clicker_name", "clicker_ip", "clicked_at")
    list_filter = ("clicked_at",)
    search_fields = (
        "artist__user__email",
        "artist__stage_name",
        "clicker__email",
        "clicker_ip",
    )
    readonly_fields = ("clicked_at",)

    def artist_name(self, obj):
        return obj.artist.get_display_name()

    artist_name.short_description = _("Artiste")

    def clicker_name(self, obj):
        return obj.clicker.get_full_name() if obj.clicker else "Anonyme"

    clicker_name.short_description = _("Utilisateur")


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    """
    Administration pour les requêtes de recherche
    """

    list_display = ("query", "user_name", "results_count", "user_ip", "searched_at")
    list_filter = ("searched_at", "results_count")
    search_fields = ("query", "user__email", "user_ip")
    readonly_fields = ("searched_at",)

    def user_name(self, obj):
        return obj.user.get_full_name() if obj.user else "Anonyme"

    user_name.short_description = _("Utilisateur")
