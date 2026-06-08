#!/bin/sh

set -e

echo "🚀 Initialisation TalentZik..."

# Attendre que la base de données soit prête
python manage.py wait_for_db

# Collecter les fichiers statiques
echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# Exécuter les migrations
echo "📊 Migrations de la base de données..."
python manage.py migrate

# Peupler les données initiales (si la commande existe)
echo "🌱 Peuplement des données initiales..."
if python manage.py help populate_initial_data > /dev/null 2>&1; then
    python manage.py populate_initial_data || echo "⚠️ Erreur lors du peuplement, continuons sans..."
else
    echo "⚠️ Commande populate_initial_data non trouvée"
fi

echo "👤 Création du superuser depuis l'environnement..."
if python manage.py help create_superuser_from_env > /dev/null 2>&1; then
    python manage.py create_superuser_from_env || echo "⚠️ Erreur lors de la création du superuser, continuons sans..."
else
    echo "⚠️ Commande create_superuser_from_env non trouvée"
fi


echo "🎉 Initialisation terminée !"
echo "🚀 Démarrage de l'application..."

# Démarrer l'application avec Gunicorn
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers=2 --threads=4
