"""
Django command to wait for DB
"""
import time

from psycopg2 import OperationalError as Psycog2Error

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """Django command to wait for DB"""

    def handle(self, *args, **kwargs):
        """ENtrypoit for command"""
        self.stdout.write("Waiting for database")
        db_up = False
        while db_up is False:
            try:
                self.check(databases=["default"])
                db_up = True
            except (Psycog2Error, OperationalError):
                self.stdout.write("Database not available, waiting for 1 second")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Database is available"))
        