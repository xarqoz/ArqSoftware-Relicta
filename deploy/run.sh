#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# run.sh — Configura el .env con la IP pública de la EC2 y levanta el stack.
#
# Uso (dentro de la instancia EC2, desde la raíz del repo):
#   chmod +x deploy/run.sh
#   ./deploy/run.sh
#
# Detecta automáticamente la IP pública de la instancia (metadata de AWS) y la
# inyecta en DJANGO_CSRF_TRUSTED_ORIGINS para que el admin y los formularios
# funcionen. Luego construye y levanta todos los contenedores en segundo plano.
# ═══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

PORT="${NGINX_HOST_PORT:-8080}"

echo "▶ Obteniendo la IP pública de la instancia EC2..."
# IMDSv2 (requiere token). Si falla, se pide manualmente.
TOKEN="$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
    -H "X-aws-ec2-metadata-token-ttl-seconds: 300" || true)"
PUBLIC_IP="$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
    http://169.254.169.254/latest/meta-data/public-ipv4 || true)"

if [ -z "${PUBLIC_IP:-}" ]; then
    read -r -p "No se detectó la IP automáticamente. Ingrésala manualmente: " PUBLIC_IP
fi

echo "▶ IP pública: $PUBLIC_IP  (puerto $PORT)"

# ── Generar el archivo .env ──
echo "▶ Generando .env..."
cat > .env <<EOF
# Generado por deploy/run.sh — $(date)
NGINX_HOST_PORT=${PORT}

DJANGO_SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || echo "cambia-esta-clave-$(date +%s)")
DEBUG=0
ENV_TYPE=PROD
DJANGO_ALLOWED_HOSTS=${PUBLIC_IP},localhost,127.0.0.1,django_web,0.0.0.0,nginx
DJANGO_CSRF_TRUSTED_ORIGINS=http://${PUBLIC_IP}:${PORT},http://localhost:${PORT}

FLASK_ENV=production
DATABASE_URL=sqlite:////app/data/pagos.db
PORT=5000

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

ALIADO_API_URL=https://fakestoreapi.com/products?limit=5
EOF

echo "▶ Construyendo y levantando los contenedores..."
docker compose up --build -d

echo ""
echo "✓ Stack desplegado."
echo "  Accede en:  http://${PUBLIC_IP}:${PORT}/"
echo ""
echo "  Ver estado:  docker compose ps"
echo "  Ver logs:    docker compose logs -f"
echo "  Crear admin: docker compose exec django_web python manage.py createsuperuser"
echo ""
echo "⚠ Asegúrate de haber abierto el puerto ${PORT} (TCP) en el Security Group."
