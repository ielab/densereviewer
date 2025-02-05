#!/bin/bash

# Navigate to the Django application directory
cd /app/backend/src;

# Run migrations
echo "Running migrations...";
python manage.py migrate;
sleep 2;

# Start the Gunicorn server in the background
echo "Starting Gunicorn server...";
gunicorn dense_review.wsgi:application --bind=0.0.0.0:8000 &

# Wait until Gunicorn is ready
echo "Waiting for Gunicorn to start...";
while ! curl --silent 'http://13.55.69.197:8001/' > /dev/null; do
  echo "Waiting for server...";
  sleep 2;
done

echo "Server is ready. Testing API...";

# Test the API
curl --location 'http://13.55.69.197:8001/encoder/initial_request'

# Keep the container running (important for debugging or manual testing)
tail -f /dev/null
