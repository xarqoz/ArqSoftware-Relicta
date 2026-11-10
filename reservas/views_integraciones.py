"""
Vistas de Integración — Entrega 2.

Incluye:
  1. Servicio a Proveer  → endpoint JSON con información del sistema.
  2. Servicio a Consumir → consume la API del equipo aliado.
  3. API de Terceros     → consumo vía Patrón Adapter (conversión de moneda).
  4. Tareas asíncronas   → dispara trabajos de fondo con Celery/Redis.
  5. Dashboard           → frontend interactivo que integra todo lo anterior.
"""

import platform
from datetime import datetime, timezone

from django.conf import settings
from django.shortcuts import render
from django.utils.translation import gettext as _
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Reserva, Producto, Orden, Pago
from .integrations.adapters import obtener_adaptador_tasas
from .integrations.aliado_client import AliadoClient
from .tasks import generar_reporte_reservas, enviar_notificacion_reserva


# ── 1. SERVICIO A PROVEER ───────────────────────────────────────────────────
class InfoSistemaView(APIView):
    """Expone información relevante del sistema en JSON.

    Este es el endpoint que el EQUIPO ALIADO consumirá desde su aplicación.
    """

    def get(self, request):
        data = {
            "sistema": "Relicta — Reservas de Piezas de Colección",
            "equipo": "ArqSoftware-Relicta",
            "version": "2.0",
            "arquitectura": "Híbrida (Django monolito + Flask microservicio)",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "runtime": {
                "python": platform.python_version(),
                "plataforma": platform.system(),
            },
            "metricas": {
                "total_productos": Producto.objects.count(),
                "total_reservas": Reserva.objects.count(),
                "total_ordenes": Orden.objects.count(),
                "total_pagos": Pago.objects.count(),
            },
            "servicios": {
                "monolito_django": "/api/v1/",
                "microservicio_pagos_flask": "/api/v2/pagos/",
            },
        }
        return Response(data, status=status.HTTP_200_OK)


# ── 2. SERVICIO A CONSUMIR (equipo aliado) ──────────────────────────────────
class ConsumoAliadoView(APIView):
    """Consume el endpoint de información del equipo aliado y lo retorna."""

    def get(self, request):
        cliente = AliadoClient(base_url=settings.ALIADO_API_URL)
        resultado = cliente.obtener_info()
        codigo = status.HTTP_200_OK if resultado["disponible"] else status.HTTP_502_BAD_GATEWAY
        return Response(resultado, status=codigo)


# ── 3. API DE TERCEROS vía ADAPTER ──────────────────────────────────────────
class ConversionMonedaView(APIView):
    """Convierte montos entre monedas usando el Patrón Adapter.

    Query params:
      - monto   (float)  monto a convertir   (default: 100)
      - origen  (str)    moneda origen        (default: USD)
      - destino (str)    moneda destino       (default: COP)
    """

    def get(self, request):
        try:
            monto = float(request.query_params.get("monto", 100))
        except (TypeError, ValueError):
            return Response(
                {"error": _("El parámetro 'monto' debe ser numérico")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        origen = request.query_params.get("origen", "USD")
        destino = request.query_params.get("destino", "COP")

        adaptador = obtener_adaptador_tasas()
        try:
            resultado = adaptador.convertir(monto, origen, destino)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(resultado, status=status.HTTP_200_OK)


# ── 4. TAREAS ASÍNCRONAS (Celery + Redis) ───────────────────────────────────
class DispararReporteView(APIView):
    """Encola la generación asíncrona de un reporte de reservas."""

    def post(self, request):
        tarea = generar_reporte_reservas.delay()
        return Response(
            {
                "mensaje": _("Reporte encolado. Se procesará en segundo plano."),
                "task_id": tarea.id,
                "estado": "PENDING",
            },
            status=status.HTTP_202_ACCEPTED,
        )


class DispararNotificacionView(APIView):
    """Encola el envío asíncrono de una notificación de reserva."""

    def post(self, request):
        reserva_id = request.data.get("reserva_id", 0)
        email = request.data.get("email", "demo@relicta.com")
        tarea = enviar_notificacion_reserva.delay(reserva_id, email)
        return Response(
            {
                "mensaje": _("Notificación encolada para envío asíncrono."),
                "task_id": tarea.id,
                "estado": "PENDING",
            },
            status=status.HTTP_202_ACCEPTED,
        )


# ── 5. DASHBOARD (frontend interactivo) ─────────────────────────────────────
def dashboard(request):
    """Renderiza el panel de control interactivo del sistema."""
    contexto = {
        "total_productos": Producto.objects.count(),
        "total_reservas": Reserva.objects.count(),
        "total_ordenes": Orden.objects.count(),
        "total_pagos": Pago.objects.count(),
        "productos": Producto.objects.all()[:12],
        "reservas": Reserva.objects.select_related("producto", "usuario").all()[:10],
    }
    return render(request, "dashboard.html", contexto)
