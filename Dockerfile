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

# Instalar solo las dependencias esenciales de Django
# (se excluyen matplotlib, jupyter, etc. que son para notebooks locales)
# djangorestframework se deja sin pin exacto para que pip elija la versión
# compatible con Django 6.0 (evita fallos por pins inexistentes).
COPY requirements.txt .
RUN pip install --no-cache-dir \
    "Django>=6.0,<6.1" \
    djangorestframework \
    gunicorn==23.0.0

# Copiar código fuente
COPY . .

# Ejecutar migraciones y luego levantar con Gunicorn
EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --no-input && gunicorn relicta.wsgi:application --bind 0.0.0.0:8000 --workers 2"]
