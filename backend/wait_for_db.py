#!/usr/bin/env python3
"""Wait for PostgreSQL to be ready, run init_db, then execute the remaining command"""
import socket
import time
import sys
import os
import subprocess

host = os.environ.get("DB_HOST", "postgres")
port = int(os.environ.get("DB_PORT", "5432"))
max_wait = 60

print(f"Waiting for PostgreSQL at {host}:{port}...")
for i in range(max_wait):
    try:
        s = socket.create_connection((host, port), timeout=1)
        s.close()
        print(f"PostgreSQL is ready after {i+1} seconds!")
        break
    except Exception:
        time.sleep(1)
else:
    print("WARNING: PostgreSQL not ready after 60s, continuing anyway...")

# Run init_db
print("Initializing database...")
sys.path.insert(0, "/app")
try:
    from database import init_db
    init_db()
    print("Database initialized successfully!")
except Exception as e:
    print(f"Database init error: {e}")
    sys.exit(1)

# Execute remaining command arguments
if len(sys.argv) > 1:
    cmd = sys.argv[1:]
    print(f"Starting: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    sys.exit(result.returncode)
