class ReservaBuilder:
    """Construye una Reserva paso a paso, validando disponibilidad antes de guardar."""

    def __init__(self):
        self._usuario = None
        self._producto = None
        self._fecha_limite = None
        self._monto_anticipo = None

    def para_usuario(self, usuario):
        self._usuario = usuario
        return self

    def para_producto(self, producto):
        self._producto = producto
        return self

    def con_fecha_limite(self, fecha):
        self._fecha_limite = fecha
        return self

    def con_anticipo(self, monto):
        self._monto_anticipo = monto
        return self

    def build(self):
        if not self._usuario or not self._producto:
            raise ValueError("Usuario y producto son obligatorios para crear la reserva")
        if not self._fecha_limite or self._monto_anticipo is None:
            raise ValueError("Fecha límite y monto de anticipo son obligatorios")
        if not self._producto.validar_stock(1):
            raise ValueError("El producto no tiene stock disponible para reservar")

        from reservas.models import Reserva
        reserva = Reserva(
            usuario=self._usuario,
            producto=self._producto,
            fecha_limite=self._fecha_limite,
            monto_anticipo=self._monto_anticipo,
        )
        reserva.full_clean()
        return reserva