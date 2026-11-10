"""
Configuración de Celery para comunicación asíncrona.

Celery usa Redis como Message Broker para procesar tareas en segundo plano
(reportes pesados, notificaciones por email, etc.) sin bloquear el hilo
principal de Django.
"""

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "relicta.settings")

app = Celery("relicta")

# Lee la configuración desde settings.py con el prefijo CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Descubre automáticamente las tareas en tasks.py de cada app instalada.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
