# TalentZik 🎵

TalentZik est une plateforme web moderne conçue pour connecter les artistes (musiciens, chanteurs, groupes, DJ, etc.) avec des recruteurs, des organisateurs d'événements et des passionnés de musique. Elle permet aux artistes de créer des profils professionnels riches, de présenter leurs portfolios multimédias et de recevoir des avis certifiés de clients.

---

## Objectifs et Problématique

### 1. La Problématique
Le secteur de l'événementiel musical souffre d'un manque de centralisation et de transparence :
*   Les organisateurs d'événements ont du mal à trouver, évaluer et contacter des talents de manière fiable.
*   Les artistes manquent de plateformes dédiées pour présenter proprement des contenus multimédias (audios, vidéos, photos, documents)
*   L'absence d'un système d'évaluation structuré rend difficile la validation des compétences professionnelles d'un artiste avant sa réservation.

### 2. Les Solutions apportées par TalentZik
*   **Portfolios Multimédias Riches :** Support natif pour l'hébergement de fichiers audio, vidéo, photo, et de documents de presse/tarifs (avec gestion des tailles maximales : 25 Mo pour l'audio, 100 Mo pour la vidéo).
*   **Profils Artistes Détaillés :** Présentation des bios, des genres musicaux, des compétences, des liens externes et des disponibilités.
*   **Système d'Avis et d'Évaluations :** Un mécanisme pour permettre aux organisateurs de laisser des notes et commentaires constructifs.
*   **Interface Responsive Premium :** Un design élégant basé sur TailwindCSS, assurant une navigation fluide sur mobile comme sur ordinateur.

---

## 🛠️ Pile Technique

*   **Framework Principal :** Django 4.2 (Python 3.11)
*   **Interface Utilisateur :** TailwindCSS, Django Crispy Forms (Crispy Tailwind)
*   **Base de Données :** 
    *   *Développement :* SQLite (léger, sans configuration externe)
    *   *Production :* PostgreSQL (robuste et performant)
*   **Gestion des Tâches Asynchrones :** Celery (pour l'envoi d'e-mails et le traitement asynchrone des médias lourds)
*   **Broker & Cache :** Redis (gestion des sessions, cache applicatif et files d'attente Celery)
*   **Serveur Web de Production :** Nginx (proxy inverse et serveur direct de fichiers statiques/médias)
*   **Déploiement :** Dokploy (PaaS Docker-native hébergé sur VPS)

---

## 🚀 Installation et Démarrage Local

### Prérequis
*   Python 3.11 ou supérieur
*   Docker et Docker Compose (pour tester l'architecture complète)

---

### Option 1 : Lancement en mode Développement (Léger & Rapide)
Cette méthode utilise **SQLite** et ne nécessite ni PostgreSQL ni Docker. Elle est recommandée pour le développement rapide de fonctionnalités.

1.  **Cloner le projet et copier le fichier d'environnement :**
    ```bash
    cp .env.example .env
    ```

2.  **Configurer le fichier `.env` :**
    Ouvrez le fichier `.env` et assurez-vous d'avoir les lignes suivantes configurées :
    ```env
    DJANGO_SETTINGS_MODULE=config.settings.development
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1
    SECRET_KEY=votre_cle_secrete_locale
    ```

3.  **Créer et activer l'environnement virtuel :**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Sur macOS/Linux
    # ou
    venv\Scripts\activate     # Sur Windows
    ```

4.  **Installer les dépendances :**
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

5.  **Exécuter les migrations et démarrer le serveur :**
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

6.  **Accéder à l'application :**
    Rendez-vous sur [http://localhost:8000](http://localhost:8000).

---

### Option 2 : Lancement en mode Docker Compose (Complet)
Cette méthode lance l'environnement complet avec Django, PostgreSQL, Redis et Celery via Docker.

1.  **Configurer le fichier `.env` :**
    ```env
    DJANGO_SETTINGS_MODULE=config.settings.development
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1,web
    
    DB_NAME=talentzik_db
    DB_USER=talentzik_user
    DB_PASSWORD=talentzik_password
    DB_HOST=db
    DB_PORT=5432
    
    REDIS_URL=redis://redis:6379/1
    ```

2.  **Lancer les conteneurs requis pour le développement :**
    Comme Nginx nécessite des configurations SSL de production en local, démarrez uniquement les conteneurs Django, DB, Redis et Celery :
    ```bash
    docker compose up db redis web celery
    ```

3.  **Accéder à l'application :**
    Rendez-vous sur [http://localhost:8000](http://localhost:8000).
