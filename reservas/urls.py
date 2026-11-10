from django.urls import path
from .views import CrearReservaView
from .views_integraciones import (
    InfoSistemaView,
    ConsumoAliadoView,
    ConversionMonedaView,
    DispararReporteView,
    DispararNotificacionView,
)

urlpatterns = [
    # ── Reservas (lógica original del monolito) ──
    path("reservas/crear/", CrearReservaView.as_view(), name="crear_reserva"),

    # ── 1. Servicio a Proveer (consumido por el equipo aliado) ──
    path("info/", InfoSistemaView.as_view(), name="info_sistema"),

    # ── 2. Servicio a Consumir (del equipo aliado) ──
    path("aliado/", ConsumoAliadoView.as_view(), name="consumo_aliado"),

    # ── 3. API de Terceros vía Adapter (conversión de moneda) ──
    path("conversion/", ConversionMonedaView.as_view(), name="conversion_moneda"),

    # ── 4. Tareas asíncronas (Celery + Redis) ──
    path("tareas/reporte/", DispararReporteView.as_view(), name="disparar_reporte"),
    path("tareas/notificacion/", DispararNotificacionView.as_view(), name="disparar_notificacion"),
]
