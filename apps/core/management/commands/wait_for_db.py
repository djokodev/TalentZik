"""
Django command to wait for the database to be available.
"""

import time

from django.core.management.base import BaseCommand
from django.db import connections, OperationalError
from psycopg2 import OperationalError as Psycopg2OpError


class Command(BaseCommand):
    """Django command to wait for the database."""

    def handle(self, *args, **options):
        """Entrypoint for command."""
        self.stdout.write("Waiting for database...")
        db_up = False
        while db_up is False:
            try:
                # Check the default database connection
                connection = connections["default"]
                connection.ensure_connection()  # Tries to open the connection
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write("Database unavailable, waiting 1 second...")
                time.sleep(1)
            finally:
                # Ensure connection is closed if it was established
                if connection and connection.connection:
                    connection.close()

        self.stdout.write(self.style.SUCCESS("Database available!"))
