"""
Patrón Adapter — Inversión de Dependencias para APIs de terceros.

El dominio depende de la ABSTRACCIÓN (TasaCambioPort), no de la
implementación concreta de la API externa. Esto permite:
  - Cambiar el proveedor de tasas de cambio sin tocar la lógica de negocio.
  - Testear con un adaptador falso (StubTasaCambioAdapter).
  - Aislar los fallos de la API externa (resiliencia).

Estructura:
    TasaCambioPort (interfaz)  ◄─── ReservaService / Vistas (dominio)
         ▲
         │ implementa
    ExchangeRateApiAdapter  ───► API de terceros (open.er-api.com)
    StubTasaCambioAdapter   ───► valores fijos (fallback / tests)
"""

from abc import ABC, abstractmethod
import logging

import requests

logger = logging.getLogger(__name__)


# ── PUERTO (Abstracción) ──────────────────────────────────────────────────────
class TasaCambioPort(ABC):
    """Interfaz que el dominio usa para obtener tasas de cambio.

    El dominio NO sabe qué proveedor hay detrás (Inversión de Dependencias).
    """

    @abstractmethod
    def convertir(self, monto: float, origen: str, destino: str) -> dict:
        """Convierte `monto` de la moneda `origen` a la moneda `destino`.

        Retorna un dict normalizado:
            {
              "monto_origen": float,
              "moneda_origen": str,
              "monto_convertido": float,
              "moneda_destino": str,
              "tasa": float,
              "proveedor": str,
            }
        """
        raise NotImplementedError


# ── ADAPTADOR CONCRETO (API de terceros real) ──────────────────────────────────
class ExchangeRateApiAdapter(TasaCambioPort):
    """Adapta la API pública open.er-api.com a la interfaz TasaCambioPort.

    Traduce el formato propio de la API externa al formato que espera el dominio.
    No requiere API key (endpoint público y gratuito).
    """

    BASE_URL = "https://open.er-api.com/v6/latest"

    def __init__(self, timeout: int = 5, fallback: "TasaCambioPort | None" = None):
        self.timeout = timeout
        # Resiliencia: si la API externa falla, se usa el fallback (stub).
        self.fallback = fallback or StubTasaCambioAdapter()

    def convertir(self, monto: float, origen: str, destino: str) -> dict:
        origen = origen.upper()
        destino = destino.upper()
        try:
            resp = requests.get(f"{self.BASE_URL}/{origen}", timeout=self.timeout)
            resp.raise_for_status()
            payload = resp.json()

            rates = payload.get("rates", {})
            if destino not in rates:
                raise ValueError(f"Moneda destino '{destino}' no soportada por el proveedor")

            tasa = float(rates[destino])
            convertido = round(monto * tasa, 2)

            # ── Traducción al formato normalizado del dominio ──
            return {
                "monto_origen": monto,
                "moneda_origen": origen,
                "monto_convertido": convertido,
                "moneda_destino": destino,
                "tasa": tasa,
                "proveedor": "open.er-api.com",
            }
        except (requests.RequestException, ValueError, KeyError) as exc:
            # ── Resiliencia: degradación elegante al fallback ──
            logger.warning("Fallo en API de tasas (%s). Usando fallback.", exc)
            resultado = self.fallback.convertir(monto, origen, destino)
            resultado["proveedor"] = f"fallback ({resultado['proveedor']})"
            return resultado


# ── ADAPTADOR STUB (fallback / tests) ──────────────────────────────────────────
class StubTasaCambioAdapter(TasaCambioPort):
    """Adaptador con tasas fijas. Sirve de fallback y para pruebas offline."""

    # Tasas aproximadas respecto a USD (solo para degradación / demo).
    _TASAS_USD = {
        "USD": 1.0,
        "EUR": 0.92,
        "COP": 4000.0,
        "MXN": 17.0,
        "GBP": 0.79,
    }

    def convertir(self, monto: float, origen: str, destino: str) -> dict:
        origen = origen.upper()
        destino = destino.upper()

        if origen not in self._TASAS_USD or destino not in self._TASAS_USD:
            raise ValueError("Moneda no soportada por el adaptador stub")

        # Convertir origen→USD→destino
        monto_usd = monto / self._TASAS_USD[origen]
        convertido = round(monto_usd * self._TASAS_USD[destino], 2)
        tasa = round(self._TASAS_USD[destino] / self._TASAS_USD[origen], 6)

        return {
            "monto_origen": monto,
            "moneda_origen": origen,
            "monto_convertido": convertido,
            "moneda_destino": destino,
            "tasa": tasa,
            "proveedor": "stub-local",
        }


# ── FACTORY (selección del adaptador) ──────────────────────────────────────────
def obtener_adaptador_tasas() -> TasaCambioPort:
    """Punto único de construcción del adaptador de tasas de cambio.

    Permite cambiar el proveedor en un solo lugar (Inversión de Dependencias).
    """
    return ExchangeRateApiAdapter()
