#!/bin/bash

# Esperar a que PostgreSQL esté listo
echo "Waiting for PostgreSQL to be ready..."
while ! nc -z postgres 5432; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Esperar a que Redis esté listo
echo "Waiting for Redis to be ready..."
while ! nc -z redis 6379; do
  sleep 1
done
echo "Redis is ready!"

# Ejecutar migraciones
echo "Running database migrations..."
alembic upgrade head || echo "Migration failed, continuing..."

# Iniciar la aplicación
echo "Starting FastAPI application..."
uvicorn main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 600