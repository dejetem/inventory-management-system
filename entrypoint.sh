#!/bin/bash

# Wait for database to be ready
python manage.py wait_for_db

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Start server
echo "Starting server"
gunicorn inventory_system.wsgi:application --bind 0.0.0.0:$PORT