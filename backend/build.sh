#!/usr/bin/env bash
# exit on error
set -o errexit

cd backend

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

# Seed the database with default data (idempotent, safe to run on every deploy)
python manage.py seed_db
