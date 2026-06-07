#!/bin/sh
set -e
mkdir -p logs staticfiles media
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py seed_demo --if-empty
exec gunicorn protech_project.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers 3
