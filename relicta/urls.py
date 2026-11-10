from django.contrib import admin
from django.urls import path, include
from reservas.views_integraciones import dashboard, crear_reserva_web

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── Dashboard interactivo (frontend) en la raíz ──
    path('', dashboard, name='dashboard'),

    # ── Formulario web para crear reservas ──
    path('reservar/', crear_reserva_web, name='crear_reserva_web'),

    # ── API v1 — monolito Django ──
    path('api/v1/', include("reservas.urls")),

    # ── Compatibilidad: mantiene /api/ para rutas legacy ──
    path('api/', include("reservas.urls")),

    # ── Selector de idioma (i18n set_language) ──
    path('i18n/', include('django.conf.urls.i18n')),
]
