"""
Create a superuser from environment variables when available.
The command is idempotent and safe to run repeatedly.
"""

from __future__ import annotations

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = (
        "Crée un superutilisateur depuis les variables d'environnement si nécessaire."
    )

    def handle(self, *args, **options):
        user_model = get_user_model()

        email = (os.getenv("DJANGO_SUPERUSER_EMAIL") or "").strip()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD") or ""
        first_name = (os.getenv("DJANGO_SUPERUSER_FIRST_NAME") or "").strip()
        last_name = (os.getenv("DJANGO_SUPERUSER_LAST_NAME") or "").strip()

        if not email or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Variables manquantes: DJANGO_SUPERUSER_EMAIL et/ou "
                    "DJANGO_SUPERUSER_PASSWORD. Superuser non créé."
                )
            )
            return

        if not first_name or not last_name:
            self.stdout.write(
                self.style.WARNING(
                    "DJANGO_SUPERUSER_FIRST_NAME et/ou DJANGO_SUPERUSER_LAST_NAME "
                    "sont absentes. Le superuser sera créé avec des valeurs vides si besoin."
                )
            )

        existing_user = user_model.objects.filter(email__iexact=email).first()
        if existing_user is not None:
            if existing_user.is_superuser:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Superuser déjà présent pour {existing_user.email}. Aucune action."
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Un utilisateur existe déjà pour {existing_user.email} "
                        "mais n'est pas superuser. Création ignorée."
                    )
                )
            return

        with transaction.atomic():
            user = user_model.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type="organizer",
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Superuser créé avec succès: {user.email}"
            )
        )
