#!/usr/bin/env python
"""
Vérification rapide de la configuration HTTPS pour TalentZik
"""

import os
from decouple import config

print("🔍 VÉRIFICATION CONFIGURATION HTTPS")
print("=" * 40)

# Vérifier les variables d'environnement critiques
csrf_origins = config("CSRF_TRUSTED_ORIGINS", default="")
allowed_hosts = config("ALLOWED_HOSTS", default="")

print(f"CSRF_TRUSTED_ORIGINS: {csrf_origins}")
print(f"ALLOWED_HOSTS: {allowed_hosts}")

if not csrf_origins:
    print("❌ CSRF_TRUSTED_ORIGINS manquant !")
    print("Ajoutez: CSRF_TRUSTED_ORIGINS=https://votre-domaine.com")
else:
    print("✅ CSRF_TRUSTED_ORIGINS configuré")

if not allowed_hosts:
    print("❌ ALLOWED_HOSTS manquant !")
    print("Ajoutez: ALLOWED_HOSTS=votre-domaine.com,votre-ip")
else:
    print("✅ ALLOWED_HOSTS configuré")

print("\n📝 TEMPLATE DE CONFIGURATION:")
print("CSRF_TRUSTED_ORIGINS=https://votredomaine.com")
print("ALLOWED_HOSTS=votredomaine.com,192.168.1.100")
