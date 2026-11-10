# ── Microservicio de Pagos (Flask) ────────────────────────────────────────────
# Imagen ligera; solo contiene las dependencias de este servicio,
# completamente aislado del monolito Django.

FROM python:3.11-slim

# Metadatos
LABEL maintainer="ArqSoftware-Relicta"
LABEL description="Microservicio de Pagos — Strangler Pattern"

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=5000

WORKDIR /app

# Dependencias del sistema (mínimas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Puerto expuesto
EXPOSE 5000

# Levantar con Gunicorn (WSGI de producción)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "60", "app:app"]
