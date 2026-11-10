# ── Monolito Django ───────────────────────────────────────────────────────────
# Django 6.0 requiere Python 3.12+ (no soporta 3.11).
FROM python:3.12-slim

LABEL maintainer="ArqSoftware-Relicta"
LABEL description="Monolito Django — Reservas"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias desde requirements.txt
# (Django, DRF, Gunicorn, Celery, Redis, requests).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Preparar directorio de estáticos y volumen de datos
RUN mkdir -p /app/data /app/staticfiles

# Ejecutar migraciones, recolectar estáticos y levantar con Gunicorn
EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --no-input && python manage.py collectstatic --no-input && gunicorn relicta.wsgi:application --bind 0.0.0.0:8000 --workers 2"]
