from reservas.domain.reserva_builder import ReservaBuilder
from reservas.infra.notificador_factory import NotificadorFactory


class ReservaService:
    def __init__(self, notificador=None):
        self.notificador = notificador or NotificadorFactory.crear()

    def crear_reserva(self, datos):
        reserva = (
            ReservaBuilder()
            .para_usuario(datos["usuario"])
            .para_producto(datos["producto"])
            .con_fecha_limite(datos["fecha_limite"])
            .con_anticipo(datos["monto_anticipo"])
            .build()
        )
        reserva.save()
        self.notificador.enviar_confirmacion(reserva)
        return reserva