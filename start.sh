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

# Precargar modelos ML en segundo plano (opcional, no bloquea el inicio)
echo "Preloading ML models in background..."
python scripts/preload_models.py &
PRELOAD_PID=$!

# Iniciar la aplicación con configuraciones de timeout optimizadas
echo "Starting FastAPI application with optimized timeout settings..."
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 2 \
  --timeout-keep-alive 300 \
  --timeout-graceful-shutdown 300 \
  --limit-concurrency 100 \
  --limit-max-requests 1000 \
  --backlog 2048

# Si la aplicación se detiene, terminar el proceso de precarga
if [ ! -z "$PRELOAD_PID" ]; then
  kill $PRELOAD_PID 2>/dev/null || true
fi 