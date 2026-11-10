#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# setup-ec2.sh — Instala Docker + Docker Compose en una instancia EC2 nueva.
#
# Uso (dentro de la instancia EC2, una sola vez):
#   chmod +x deploy/setup-ec2.sh
#   ./deploy/setup-ec2.sh
#
# Soporta Amazon Linux 2023 / Amazon Linux 2 (yum/dnf) y Ubuntu (apt).
# Tras ejecutarlo, CIERRA y vuelve a abrir la sesión SSH para que el grupo
# 'docker' tome efecto (o usa 'newgrp docker').
# ═══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

echo "▶ Detectando sistema operativo..."

if command -v dnf >/dev/null 2>&1; then
    # ── Amazon Linux 2023 ──
    echo "▶ Amazon Linux (dnf)"
    sudo dnf update -y
    sudo dnf install -y docker git
elif command -v yum >/dev/null 2>&1; then
    # ── Amazon Linux 2 ──
    echo "▶ Amazon Linux 2 (yum)"
    sudo yum update -y
    sudo yum install -y docker git
elif command -v apt-get >/dev/null 2>&1; then
    # ── Ubuntu / Debian ──
    echo "▶ Ubuntu/Debian (apt)"
    sudo apt-get update -y
    sudo apt-get install -y docker.io git
else
    echo "✗ Gestor de paquetes no soportado. Instala Docker manualmente."
    exit 1
fi

echo "▶ Habilitando y arrancando el servicio Docker..."
sudo systemctl enable docker
sudo systemctl start docker

echo "▶ Añadiendo el usuario actual al grupo 'docker'..."
sudo usermod -aG docker "$USER"

# ── Instalar el plugin docker compose (v2) si no viene incluido ──
if ! docker compose version >/dev/null 2>&1; then
    echo "▶ Instalando el plugin docker compose v2..."
    DOCKER_CONFIG="${DOCKER_CONFIG:-$HOME/.docker}"
    mkdir -p "$DOCKER_CONFIG/cli-plugins"
    ARCH="$(uname -m)"
    curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-${ARCH}" \
        -o "$DOCKER_CONFIG/cli-plugins/docker-compose"
    chmod +x "$DOCKER_CONFIG/cli-plugins/docker-compose"
fi

echo ""
echo "✓ Instalación completada."
echo "  Docker:  $(sudo docker --version)"
echo "  Compose: $(sudo docker compose version 2>/dev/null || echo 'reinicia sesión y verifica')"
echo ""
echo "⚠ IMPORTANTE: cierra esta sesión SSH y vuelve a entrar (o ejecuta 'newgrp docker')"
echo "  para poder usar 'docker' sin sudo. Luego ejecuta: ./deploy/run.sh"
