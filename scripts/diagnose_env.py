#!/usr/bin/env python
"""
Diagnostic complet des variables d'environnement pour TalentZik
"""

import os
import sys
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, os.path.join(BASE_DIR, "apps"))

print("🔍 DIAGNOSTIC ENVIRONNEMENT COMPLET")
print("=" * 50)

# 1. Vérifier le fichier .env
env_file = BASE_DIR / ".env"
print(f"📁 Fichier .env existe: {env_file.exists()}")
if env_file.exists():
    print(f"📍 Chemin .env: {env_file}")
    with open(env_file, "r") as f:
        lines = f.readlines()
    print(f"📏 Nombre de lignes dans .env: {len(lines)}")

    # Afficher les variables importantes (sans les valeurs sensibles)
    important_vars = ["DEBUG", "ALLOWED_HOSTS", "CSRF_TRUSTED_ORIGINS"]
    for line in lines:
        if any(var in line for var in important_vars):
            print(f"   {line.strip()}")

# 2. Vérifier les variables d'environnement système
print(f"\n🌍 VARIABLES D'ENVIRONNEMENT SYSTÈME:")
important_vars = [
    "DEBUG",
    "ALLOWED_HOSTS",
    "CSRF_TRUSTED_ORIGINS",
    "DJANGO_SETTINGS_MODULE",
]
for var in important_vars:
    value = os.environ.get(var, "NON DÉFINIE")
    print(f"   {var}: {value}")

# 3. Tester decouple
print(f"\n🔧 TEST DE DECOUPLE:")
try:
    from decouple import config

    debug_from_decouple = config("DEBUG", default=None)
    allowed_hosts_from_decouple = config("ALLOWED_HOSTS", default=None)
    csrf_origins_from_decouple = config("CSRF_TRUSTED_ORIGINS", default=None)

    print(f"   DEBUG via decouple: {debug_from_decouple}")
    print(f"   ALLOWED_HOSTS via decouple: {allowed_hosts_from_decouple}")
    print(f"   CSRF_TRUSTED_ORIGINS via decouple: {csrf_origins_from_decouple}")
except ImportError:
    print("   ❌ Erreur: decouple non installé")
except Exception as e:
    print(f"   ❌ Erreur decouple: {e}")

# 4. Tester les settings Django
print(f"\n⚙️  TEST DES SETTINGS DJANGO:")
try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
    import django

    django.setup()

    from django.conf import settings

    print(f"   DEBUG Django: {settings.DEBUG}")
    print(f"   ALLOWED_HOSTS Django: {settings.ALLOWED_HOSTS}")
    print(
        f"   CSRF_TRUSTED_ORIGINS Django: {getattr(settings, 'CSRF_TRUSTED_ORIGINS', 'NON DÉFINI')}"
    )
    print(f"   SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

except Exception as e:
    print(f"   ❌ Erreur Django: {e}")

# 5. Vérifications finales
print(f"\n🚨 RÉSUMÉ:")
if not env_file.exists():
    print("   ❌ PROBLÈME: Fichier .env introuvable")
else:
    print("   ✅ Fichier .env trouvé")

if os.environ.get("DJANGO_SETTINGS_MODULE") != "config.settings.production":
    print(
        f"   ⚠️  ATTENTION: DJANGO_SETTINGS_MODULE = {os.environ.get('DJANGO_SETTINGS_MODULE')}"
    )
else:
    print("   ✅ DJANGO_SETTINGS_MODULE correct")

print(f"\n💡 CONSEILS:")
print("   1. Vérifiez que le .env est au bon endroit")
print("   2. Vérifiez que DJANGO_SETTINGS_MODULE=config.settings.production")
print("   3. Redémarrez complètement Docker après modification du .env")
