#!/usr/bin/env bash
# exit on error
set -o errexit

cd "$(dirname "$0")"

python -m pip install -r requirements.txt

python manage.py collectstatic --no-input
