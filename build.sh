#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Install Node/Tailwind dependencies for django-tailwind
python manage.py tailwind install --no-input || echo "Tailwind install skipped or failed"

# Build Tailwind CSS
python manage.py tailwind build --no-input || echo "Tailwind build skipped or failed"

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate
