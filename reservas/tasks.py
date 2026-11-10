"""
Tareas asíncronas procesadas por Celery (vía Message Broker Redis).

Estas tareas se ejecutan en segundo plano, fuera del ciclo petición-respuesta,
evitando bloquear al usuario en operaciones pesadas (reportes, notificaciones).
"""

import time
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def enviar_notificacion_reserva(reserva_id, email):
    """Simula el envío asíncrono de un correo de confirmación de reserva.

    En producción aquí iría la integración con SendGrid/SES. Al ser asíncrona,
    el usuario recibe la respuesta HTTP de inmediato sin esperar al email.
    """
    logger.info("Enviando notificación de reserva #%s a %s", reserva_id, email)
    time.sleep(2)  # Simula latencia de un proveedor de email externo.
    logger.info("Notificación de reserva #%s enviada.", reserva_id)
    return {"reserva_id": reserva_id, "email": email, "estado": "enviado"}


@shared_task
def generar_reporte_reservas():
    """Simula la generación de un reporte pesado de reservas en segundo plano.

    Proceso típico que bloquearía el monolito si fuera síncrono; aquí se delega
    al worker de Celery.
    """
    logger.info("Generando reporte de reservas...")
    time.sleep(5)  # Simula un proceso intensivo (agregaciones, PDF, etc.).
    from .models import Reserva

    total = Reserva.objects.count()
    por_estado = {
        estado: Reserva.objects.filter(estado=estado).count()
        for estado, _ in Reserva.ESTADOS
    }
    reporte = {"total_reservas": total, "por_estado": por_estado}
    logger.info("Reporte generado: %s", reporte)
    return reporte
