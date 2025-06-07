"""
Configuration pour l'environnement de test/staging
Utilise SQLite pour des déploiements de test rapides
"""

from .base import *

# Debug désactivé mais logging verbeux
DEBUG = False

# Base de données SQLite optimisée pour les tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": {
            # Optimisations SQLite pour éviter les problèmes de concurrence
            "timeout": 30,
            "init_command": """
                PRAGMA journal_mode=WAL;
                PRAGMA synchronous=NORMAL;
                PRAGMA foreign_keys=ON;
                PRAGMA temp_store=MEMORY;
                PRAGMA cache_size=-64000;
            """,
        },
    }
}

# Cache simple mais fonctionnel
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
        "TIMEOUT": 300,
        "OPTIONS": {
            "MAX_ENTRIES": 1000,
        },
    }
}

# Email backend console pour voir les emails envoyés
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Session en base de données (SQLite)
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# Sécurité adaptée pour les tests (pas de HTTPS requis)
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# CORS permissif pour les tests
CORS_ALLOW_ALL_ORIGINS = True

# Logging adapté pour les tests
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "testing.log",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# Configuration spécifique pour les tests
MAX_AUDIO_SIZE = 10 * 1024 * 1024  # 10MB pour les tests
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50MB pour les tests

# Désactiver Celery en test (tâches synchrones)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

print("🧪 Configuration de test chargée - Utilisation de SQLite")
