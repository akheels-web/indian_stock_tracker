#!/bin/sh
# Wait for postgres to be ready using Python (no external deps needed)
echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
python -c "
import socket, time, os
host = os.environ.get('DB_HOST', 'postgres')
port = int(os.environ.get('DB_PORT', '5432'))
while True:
    try:
        s = socket.create_connection((host, port), timeout=1)
        s.close()
        break
    except:
        time.sleep(1)
print('PostgreSQL is ready!')
"

# Initialize database
echo "Initializing database..."
python -c "from database import init_db; init_db()"

# Start the application
echo "Starting application..."
exec "$@"
