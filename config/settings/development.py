"""
Configuration pour l'environnement de développement
"""

from .base import *

# Debug activé en développement
DEBUG = True

# Base de données SQLite pour le développement
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Email backend pour le développement (console)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Cache simple en développement
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Configuration de session pour le développement
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# Désactiver HTTPS en développement
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0

# Autoriser tous les hosts en développement
ALLOWED_HOSTS = ["*"]

# Configuration CORS permissive en développement
CORS_ALLOW_ALL_ORIGINS = True

# Logging plus verbeux en développement
LOGGING["root"]["level"] = "DEBUG"
LOGGING["loggers"]["apps"]["level"] = "DEBUG"

# Désactiver la compression des fichiers statiques
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
