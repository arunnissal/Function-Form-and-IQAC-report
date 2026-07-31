#!/usr/bin/env bash
# exit on error
set -o errexit

python manage.py migrate
python manage.py seed_data
gunicorn --bind 0.0.0.0:${PORT:-8000} function_requirement_system.wsgi:application
