from django.db import models
from django.conf import settings


class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    stock_actual = models.IntegerField(default=0)
    es_edicion_limitada = models.BooleanField(default=False)

    def validar_stock(self, cantidad):
        return self.stock_actual >= cantidad

    def __str__(self):
        return self.nombre


class Reserva(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("confirmada", "Confirmada"),
        ("expirada", "Expirada"),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fecha_limite = models.DateField()
    monto_anticipo = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    creada_en = models.DateTimeField(auto_now_add=True)

    def confirmar(self):
        self.estado = "confirmada"
        self.save()

    def expirar(self):
        self.estado = "expirada"
        self.save()

    def __str__(self):
        return f"Reserva #{self.id} - {self.producto} - {self.usuario}"