#!/bin/bash

# Wait for database to be ready
python manage.py wait_for_db

# Apply database migrations
echo "Starting Celery worker"
celery -A inventory_system worker --loglevel=info