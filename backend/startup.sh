#!/bin/sh
# Wait for postgres to be ready
echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Initialize database
echo "Initializing database..."
python -c "from database import init_db; init_db()"

# Start the application
echo "Starting application..."
exec "$@"
