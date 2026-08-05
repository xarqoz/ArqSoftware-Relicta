import os


class NotificadorBase:
    def enviar_confirmacion(self, reserva):
        raise NotImplementedError


class NotificadorEmailReal(NotificadorBase):
    def enviar_confirmacion(self, reserva):
        # Aquí iría la integración real con SendGrid/SES/etc.
        print(f"[EMAIL REAL] Confirmación enviada a {reserva.usuario.email}")


class NotificadorConsola(NotificadorBase):
    def enviar_confirmacion(self, reserva):
        print(f"[DEV] Reserva #{reserva.id} confirmada para {reserva.usuario} — pieza: {reserva.producto}")


class NotificadorFactory:
    @staticmethod
    def crear():
        if os.getenv("ENV_TYPE") == "PROD":
            return NotificadorEmailReal()
        return NotificadorConsola()