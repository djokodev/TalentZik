# Dockerfile multi-stage pour TalentZik
# Stage 1: Builder - Installation des dépendances et construction
FROM python:3.11-slim as builder

# Éviter les interactions lors de l'installation des paquets
ENV DEBIAN_FRONTEND=noninteractive

# Installer les dépendances système nécessaires pour la compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    zlib1g-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Créer un environnement virtuel
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip wheel setuptools
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production - Image finale légère
FROM python:3.11-slim as production

# Éviter les interactions lors de l'installation des paquets
ENV DEBIAN_FRONTEND=noninteractive

# Installer uniquement les dépendances runtime nécessaires
RUN apt-get update && apt-get install -y \
    libpq5 \
    libjpeg62-turbo \
    libpng16-16 \
    libwebp7 \
    zlib1g \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier l'environnement virtuel depuis le builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Configuration des variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

# Créer un utilisateur non-root pour la sécurité
RUN groupadd -r django && useradd -r -g django django

# Créer les répertoires nécessaires
RUN mkdir -p /app /app/staticfiles /app/media /app/logs && \
    chown -R django:django /app

# Définir le répertoire de travail
WORKDIR /app

# Copier le code de l'application
COPY --chown=django:django . .

# Copier et rendre exécutable le script d'initialisation
COPY --chown=django:django scripts/run.sh /app/run.sh
RUN chmod +x /app/run.sh

# Installer Gunicorn si pas déjà dans requirements.txt
RUN pip install gunicorn

# Changer vers l'utilisateur non-root
USER django

# Exposer le port 8000
EXPOSE 8000