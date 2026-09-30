# Relicta — Arquitectura Híbrida (Strangler Pattern)

Sistema de reservas de piezas de colección, migrado parcialmente a microservicios mediante el **Strangler Pattern**.

## Arquitectura

```
Cliente
  │
  ▼
Nginx :80
  ├── /api/v1/  ──▶  Django :8000  (monolito — reservas)
  └── /api/v2/pagos/  ──▶  Flask :5000  (microservicio — pagos)
```

## Levantamiento rápido

```bash
# 1. Copiar variables de entorno
cp .env.example .env

# 2. Construir y levantar todos los servicios
docker-compose up --build

# 3. Verificar servicios
curl http://localhost/api/v1/reservas/crear/    # → Django
curl http://localhost/api/v2/pagos/health       # → Flask
```

## Endpoints

### Monolito Django (`/api/v1/`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/reservas/crear/` | Crear una reserva |

### Microservicio Pagos Flask (`/api/v2/pagos/`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v2/pagos/health` | Health check del servicio |
| POST | `/api/v2/pagos/` | Procesar nuevo pago |
| GET | `/api/v2/pagos/<id>/` | Consultar pago por ID |
| GET | `/api/v2/pagos/orden/<orden_id>/` | Consultar pago por orden |
| PATCH | `/api/v2/pagos/<id>/aprobar/` | Aprobar un pago pendiente |

## Estructura del proyecto

```
ArqSoftware-Relicta/
├── relicta/              # Configuración Django
├── reservas/             # App monolito (reservas)
├── microservicio_pagos/  # Microservicio Flask (pagos)
│   ├── app.py
│   ├── models.py
│   ├── requirements.txt
│   └── Dockerfile
├── nginx/
│   └── nginx.conf        # Enrutamiento de tráfico
├── Dockerfile            # Django
├── docker-compose.yml    # Orquestación completa
└── .env.example
```

## Wiki

Ver [Migración a Microservicios (Strangler Pattern)](../../wiki/Migraci%C3%B3n-a-Microservicios-(Strangler-Pattern)) para la matriz de decisión y documentación técnica completa.
