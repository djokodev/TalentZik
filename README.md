# TalentZik 🎵

> **Conçu pour le Cameroun. Pensé pour l'Afrique.**

TalentZik est une plateforme web moderne conçue pour connecter les artistes camerounais (musiciens, chanteurs, groupes, DJ, etc.) avec des recruteurs, des organisateurs d'événements et des passionnés de musique. Pensée d'abord pour le marché camerounais, la plateforme a vocation à s'étendre progressivement à l'ensemble du continent africain, en valorisant la richesse des talents locaux souvent sous-représentés sur les plateformes internationales.

Elle permet aux artistes de créer des profils professionnels riches, de présenter leurs portfolios multimédias et de recevoir des avis certifiés de clients.

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

| Composant | Technologie | Rôle |
|---|---|---|
| **Framework** | Django 4.2 (Python 3.11) | Backend MVT, ORM, admin, auth |
| **UI / Templates** | TailwindCSS + Crispy Forms | Rendu HTML côté serveur |
| **Base de données dev** | SQLite | Léger, zéro configuration locale |
| **Base de données prod** | PostgreSQL 15 | Robuste, ACID, full-text search |
| **Tâches asynchrones** | Celery 5.3 | File d'attente pour emails, médias |
| **Broker & Cache** | Redis 7 | Sessions, cache, files Celery |
| **Serveur applicatif** | Gunicorn | WSGI multi-workers pour Django |
| **Proxy inverse** | Nginx | Sert les statiques, reverse proxy |
| **Conteneurisation** | Docker + Docker Compose | Isolation et portabilité |

---

## 🏗️ Architecture du Projet

TalentZik suit le pattern **MVT (Model – View – Template)** natif de Django, organisé en couches fonctionnelles distinctes. L'ensemble des services tourne dans des conteneurs Docker isolés et communique via un réseau interne.

### Pattern MVT — Modèle, Vue, Template

```
┌────────────────────────────────────────────────────────┐
│                     NAVIGATEUR                         │
│            (Requête HTTP : localhost:8000)              │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│                  NGINX (Port 80)                       │
│  • Sert les fichiers statiques (CSS, JS, images)       │
│  • Sert les fichiers médias uploadés par les artistes  │
│  • Redirige les autres requêtes vers Gunicorn          │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│               GUNICORN (Port 8000)                     │
│        Serveur WSGI — point d'entrée Django            │
└─────────────────────────┬──────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌──────────────┐  ┌───────────────┐  ┌──────────────────┐
│    MODÈLE    │  │     VUE       │  │    TEMPLATE      │
│  (models.py) │  │  (views.py)   │  │  (*.html)        │
│              │  │               │  │                  │
│  Artiste     │◄─┤  Logique      ├─►│  HTML rendu      │
│  Recruteur   │  │  métier       │  │  TailwindCSS     │
│  Avis        │  │  Permissions  │  │  Crispy Forms    │
│  Portfolio   │  │  Filtres      │  │                  │
└──────┬───────┘  └───────┬───────┘  └──────────────────┘
       │                  │
       ▼                  ▼
┌──────────────┐  ┌───────────────────────────────────────┐
│  PostgreSQL  │  │               REDIS                   │
│  (Port 5432) │  │            (Port 6379)                │
│              │  │  • Cache des requêtes fréquentes      │
│  Persistance │  │  • Sessions utilisateurs              │
│  de toutes   │  │  • File d'attente pour Celery         │
│  les données │  └──────────────────┬────────────────────┘
└──────────────┘                     │
                                     ▼
                        ┌────────────────────────┐
                        │    CELERY (Worker)     │
                        │  Traitement différé    │
                        │  • Envoi d'e-mails     │
                        │  • Compression médias  │
                        │  • Notifications       │
                        └────────────────────────┘
```

### Les couches en détail

#### Couche Modèle, la structure des données
Les modèles Django définissent la structure de toutes les entités métier : `Artiste`, `Recruteur`, `Portfolio`, `Avis`, `Genre musical`, etc. L'ORM Django traduit automatiquement ces classes Python en tables SQL dans PostgreSQL, sans écrire une seule ligne de SQL manuellement.

#### Couche Vue, la logique métier
Les vues Django reçoivent les requêtes HTTP, appliquent les règles métier (vérification des permissions, filtrage des artistes, validation des formulaires) et renvoient une réponse. TalentZik utilise les **Class-Based Views** (CBV) pour maximiser la réutilisabilité du code.

#### Couche Template, l'interface utilisateur
Les templates HTML sont rendus côté serveur par Django. TailwindCSS assure le design responsive et Django Crispy Forms génère automatiquement les formulaires stylisés, sans dupliquer de code HTML.

#### Traitement asynchrone, Celery + Redis
L'upload de fichiers multimédias lourds (vidéos jusqu'à 100 Mo, audios jusqu'à 25 Mo) et l'envoi d'e-mails sont des opérations longues qui ne doivent pas bloquer la réponse HTTP. Ces tâches sont placées dans une **file d'attente Redis** et traitées en arrière-plan par un **worker Celery** indépendant.

#### Isolation par conteneurs
Chaque service (Nginx, Gunicorn/Django, PostgreSQL, Redis, Celery) tourne dans son propre conteneur Docker isolé. Ils communiquent via un réseau interne nommé `talentzik_network`, sans exposer leurs ports directement sur la machine hôte (sauf Nginx sur le port 80).

---


## Installation et Démarrage Local

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
