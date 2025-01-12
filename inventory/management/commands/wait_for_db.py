import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_conn = None
        attempts = 0
        max_attempts = 30  # Maximum number of attempts (30 seconds)

        while not db_conn and attempts < max_attempts:
            try:
                db_conn = connections['default']
                db_conn.ensure_connection()  # Actively try to connect
                self.stdout.write(self.style.SUCCESS('Database available!'))
                return
            except OperationalError as e:
                self.stdout.write(f'Database unavailable, waiting 1 second... (Attempt {attempts + 1}/{max_attempts})')
                self.stdout.write(f'Error: {e}')
                time.sleep(1)
                attempts += 1

        self.stdout.write(self.style.ERROR('Database connection failed after maximum attempts.'))
        raise OperationalError('Database connection failed after maximum attempts.')