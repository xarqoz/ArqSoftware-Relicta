# Relicta — Arquitectura Híbrida y Resiliente (Entrega 2)

Sistema de reservas de piezas de colección con arquitectura de microservicios,
API Gateway, comunicación asíncrona, integraciones externas e i18n bilingüe.

## Arquitectura

```
Cliente → Nginx :8080 (API Gateway)
  ├── /  y  /api/v1/   →  Django :8000   (monolito: reservas, dashboard, integraciones)
  ├── /api/v2/pagos/   →  Flask  :5000   (microservicio de pagos — estrangulado)
  └── /static/         →  archivos estáticos

Django → Redis (broker) → Celery worker   (tareas asíncronas)
Django → API aliado + API terceros (Adapter)
```

Ver el diagrama completo en [`docs/ARQUITECTURA.md`](docs/ARQUITECTURA.md).

## Levantamiento rápido

```bash
cp .env.example .env
docker compose up --build
```

Acceder al **dashboard interactivo** en: **http://localhost:8080/**

> El puerto se controla con `NGINX_HOST_PORT` en `.env` (por defecto `8080`).

## Servicios y Endpoints

### Dashboard
| Ruta | Descripción |
|------|-------------|
| `GET /` | Panel de control interactivo (frontend) |

### Monolito Django (`/api/v1/`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/reservas/crear/` | Crear una reserva |
| GET | `/api/v1/info/` | **Servicio a Proveer** — info del sistema (JSON) |
| GET | `/api/v1/aliado/` | **Servicio a Consumir** — consume API del aliado |
| GET | `/api/v1/conversion/` | **API terceros vía Adapter** — conversión de moneda |
| POST | `/api/v1/tareas/reporte/` | Encola reporte asíncrono (Celery) |
| POST | `/api/v1/tareas/notificacion/` | Encola notificación asíncrona (Celery) |

### Microservicio Pagos Flask (`/api/v2/pagos/`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v2/pagos/health` | Health check |
| POST | `/api/v2/pagos/` | Procesar nuevo pago |
| GET | `/api/v2/pagos/<id>/` | Consultar pago por ID |
| GET | `/api/v2/pagos/orden/<orden_id>/` | Consultar pago por orden |
| PATCH | `/api/v2/pagos/<id>/aprobar/` | Aprobar pago pendiente |

## Características de la Entrega 2

- ✅ **Strangler Pattern** — pagos extraídos a microservicio Flask
- ✅ **API Gateway (Nginx)** — ruteo profesional por URL + estáticos
- ✅ **Servicio a Proveer / Consumir** — integración con equipo aliado
- ✅ **Patrón Adapter** — API de terceros con inversión de dependencias y fallback
- ✅ **Comunicación asíncrona** — Celery + Redis (Message Broker)
- ✅ **i18n bilingüe** — Español / Inglés con gettext (sin texto quemado)
- ✅ **Frontend interactivo** — dashboard con glassmorphism, animaciones y toasts
- ✅ **Docker Compose** — todo el ecosistema orquestado

## Probar las integraciones

```bash
# Servicio a proveer
curl http://localhost:8080/api/v1/info/

# Conversión de moneda (Adapter sobre API de terceros)
curl "http://localhost:8080/api/v1/conversion/?monto=100&origen=USD&destino=COP"

# Tarea asíncrona (Celery)
curl -X POST http://localhost:8080/api/v1/tareas/reporte/

# Microservicio de pagos
curl -X POST http://localhost:8080/api/v2/pagos/ \
  -H "Content-Type: application/json" \
  -d '{"orden_id": 1, "monto": 150000, "metodo": "tarjeta"}'
```

## Admin de Django

```bash
docker compose exec django_web python manage.py createsuperuser
# Luego: http://localhost:8080/admin/
```

## Estructura del proyecto

```
ArqSoftware-Relicta/
├── relicta/                  # Config Django (+ celery.py)
├── reservas/
│   ├── integrations/         # Adapter (terceros) + cliente aliado
│   ├── tasks.py              # Tareas Celery
│   ├── views_integraciones.py# Vistas de integración + dashboard
│   └── ...
├── microservicio_pagos/      # Microservicio Flask (pagos)
├── templates/                # Frontend (base.html, dashboard.html)
├── static/                   # CSS + JS del dashboard
├── locale/                   # Traducciones i18n (es / en)
├── nginx/nginx.conf          # API Gateway
├── docs/ARQUITECTURA.md      # Diagrama y documentación técnica
├── Dockerfile                # Django
├── docker-compose.yml        # Orquestación (Django, Flask, Nginx, Redis, Celery)
└── .env.example
```
