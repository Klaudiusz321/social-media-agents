#!/bin/bash
set -e

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create necessary directories if they don't exist
mkdir -p logs
mkdir -p data/analytics
mkdir -p data/reports
mkdir -p data/visualizations

# Start server
echo "Starting server..."
python manage.py runserver 0.0.0.0:8000 