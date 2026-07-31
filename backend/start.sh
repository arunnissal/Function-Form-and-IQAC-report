#!/usr/bin/env bash
# exit on error
set -o errexit

python manage.py migrate
python manage.py seed_data
gunicorn function_requirement_system.wsgi:application
