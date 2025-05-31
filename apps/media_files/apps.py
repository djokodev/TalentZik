"""
Configuration de l'application media_files
"""

from django.apps import AppConfig


class MediaFilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.media_files"
    verbose_name = "Fichiers multimédia"
