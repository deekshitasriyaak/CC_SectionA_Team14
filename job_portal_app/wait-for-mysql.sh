#!/bin/bash

# Environment variables for database connection
HOST=${JOB_DB_HOST:-"job_db"}
USER=${JOB_DB_USER:-"root"}
PASSWORD=${JOB_DB_PASSWORD:-"chandu@123S"}
DB=${JOB_DB_NAME:-"job_portal"}

# Wait for MySQL to be ready
echo "Waiting for MySQL at $HOST to be ready..."
max_tries=30
counter=0

until mysqladmin ping -h "$HOST" -u "$USER" -p"$PASSWORD" --silent; do
    counter=$((counter + 1))
    if [ $counter -ge $max_tries ]; then
        echo "Error: Couldn't connect to MySQL after $max_tries attempts."
        exit 1
    fi
    echo "MySQL is not ready yet. Waiting... ($counter/$max_tries)"
    sleep 3
done

echo "MySQL at $HOST is ready! Initializing database..."

# Execute the command passed to this script
exec "$@"