"""
Cliente para consumir el "Servicio a Consumir" del equipo aliado.

El equipo aliado expone un endpoint JSON con información de su sistema.
Este cliente lo consume y normaliza la respuesta para mostrarla en nuestra UI.

La URL del aliado es configurable vía la variable de entorno ALIADO_API_URL,
para no acoplar el código a un host concreto (resiliencia y portabilidad).
"""

import os
import logging

import requests

logger = logging.getLogger(__name__)


class AliadoClient:
    """Consume el endpoint de información del sistema del equipo aliado."""

    def __init__(self, base_url: str | None = None, timeout: int = 5):
        # Si no hay aliado configurado, se apunta a nuestro propio endpoint
        # de demostración para que la pantalla siempre tenga datos.
        self.base_url = base_url or os.getenv(
            "ALIADO_API_URL", "http://localhost:8000/api/v1/info/"
        )
        self.timeout = timeout

    def obtener_info(self) -> dict:
        """Devuelve la info del aliado o un payload de error controlado."""
        try:
            resp = requests.get(self.base_url, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return {
                "disponible": True,
                "fuente": self.base_url,
                "datos": data,
                "error": None,
            }
        except requests.RequestException as exc:
            logger.warning("No se pudo consumir el servicio aliado: %s", exc)
            return {
                "disponible": False,
                "fuente": self.base_url,
                "datos": None,
                "error": str(exc),
            }
