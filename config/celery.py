import os
from celery import Celery

# Définir le module de settings par défaut pour Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

app = Celery("talentzik")

# Utiliser une chaîne ici signifie que le worker n'a pas à sérialiser
# l'objet de configuration vers les processus enfants.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Découvrir automatiquement les tâches depuis toutes les applications installées
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Tâche de debug pour tester Celery"""
    print(f"Request: {self.request!r}")
