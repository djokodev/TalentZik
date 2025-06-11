from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Hosts autorisés en production - OBLIGATOIRE !
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="").split(",")

# Vérification que ALLOWED_HOSTS est configuré
if not ALLOWED_HOSTS or ALLOWED_HOSTS == [""]:
    raise ValueError("ALLOWED_HOSTS doit être configuré en production !")

# Base de données PostgreSQL en production
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        # Connexions persistantes pour un temps d'attente de 10 minutes
        "CONN_MAX_AGE": 600,
    }
}

# Configuration Redis pour cache et Celery
REDIS_URL = config("REDIS_URL", default="redis://localhost:6379")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"{REDIS_URL}/1",
        "KEY_PREFIX": "talentzik",
        "TIMEOUT": 300,
    }
}

# Configuration Celery
CELERY_BROKER_URL = f"{REDIS_URL}/0"
CELERY_RESULT_BACKEND = f"{REDIS_URL}/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes


# Configuration des fichiers statiques pour production
STATIC_ROOT = config("STATIC_ROOT", default="/app/staticfiles")
MEDIA_ROOT = config("MEDIA_ROOT", default="/app/media")


# Configuration email production
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT", cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL")

# Vérifier que la configuration email est complète
if not all([EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD]):
    print("⚠️  ATTENTION: Configuration email incomplète")

# Configuration CORS restrictive en production
CORS_ALLOWED_ORIGINS = []
if config("CORS_ALLOWED_ORIGINS", default=""):
    CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS").split(",")

# Logging avancé en production
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        "request": {
            "format": "{asctime} - {levelname} - {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": config("LOG_FILE", default="/app/logs/django.log"),
            "formatter": "verbose",
            "maxBytes": 1024 * 1024 * 15,  # 15MB
            "backupCount": 10,
        },
        "console": {
            "level": "DEBUG",  # Changé à DEBUG pour plus de détails
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": config("ERROR_LOG_FILE", default="/app/logs/error.log"),
            "formatter": "verbose",
            "maxBytes": 1024 * 1024 * 10,  # 10MB
            "backupCount": 5,
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": "DEBUG",  # Plus de détails
            "propagate": False,
        },
        "django.request": {
            "handlers": ["error_file", "console"],
            "level": "DEBUG",  # Capturer toutes les requêtes HTTP
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console"],
            "level": "DEBUG",  # Logs du serveur de dev
            "propagate": False,
        },
        "apps": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "celery": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Configuration de performance
USE_TZ = True
USE_I18N = True
USE_L10N = True

# Optimisations de template
TEMPLATES[0]["OPTIONS"]["debug"] = False

# Configuration HTTPS et CSRF - OBLIGATOIRE après passage en HTTPS
SECURE_SSL_REDIRECT = True  # Redirection automatique HTTP → HTTPS
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)  # Pour les proxies (nginx)

# Cookies sécurisés pour HTTPS
SESSION_COOKIE_SECURE = True  # OBLIGATOIRE avec HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# Configuration CSRF pour HTTPS
CSRF_COOKIE_SECURE = True  # OBLIGATOIRE avec HTTPS
CSRF_COOKIE_HTTPONLY = True  # Peut rester True
CSRF_COOKIE_SAMESITE = "Lax"

# Origines de confiance CSRF - CRITIQUE pour HTTPS
CSRF_TRUSTED_ORIGINS = []
if config("CSRF_TRUSTED_ORIGINS", default=""):
    CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS").split(",")

# Configuration de session pour HTTPS
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 3600  # 1 heure
SESSION_SAVE_EVERY_REQUEST = True
