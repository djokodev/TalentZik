"""
Configuration de l'application artists
"""

from django.apps import AppConfig


class ArtistsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.artists"
    verbose_name = "Artistes"
