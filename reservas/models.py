from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    stock_actual = models.IntegerField(default=0)
    es_edicion_limitada = models.BooleanField(default=False)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name="productos")

    def validar_stock(self, cantidad):
        return self.stock_actual >= cantidad

    def __str__(self):
        return self.nombre


class Orden(models.Model):
    ESTADOS = [
        ("creada", "Creada"),
        ("confirmada", "Confirmada"),
        ("cancelada", "Cancelada"),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ordenes")
    productos = models.ManyToManyField(Producto, through="OrdenItem")
    estado = models.CharField(max_length=20, choices=ESTADOS, default="creada")
    creada_en = models.DateTimeField(auto_now_add=True)

    def calcular_total(self):
        return sum(item.subtotal() for item in self.items.all())

    def confirmar(self):
        if self.estado != "creada":
            raise ValidationError("Solo una orden en estado 'creada' puede confirmarse")
        self.estado = "confirmada"
        self.save()

    def __str__(self):
        return f"Orden #{self.id} - {self.usuario}"


class OrdenItem(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario


class Pago(models.Model):
    METODOS = [("tarjeta", "Tarjeta"), ("transferencia", "Transferencia")]
    ESTADOS = [("pendiente", "Pendiente"), ("aprobado", "Aprobado"), ("rechazado", "Rechazado")]

    orden = models.OneToOneField(Orden, on_delete=models.CASCADE, related_name="pago")
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=20, choices=METODOS)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")

    def aprobar(self):
        self.estado = "aprobado"
        self.save()

    def __str__(self):
        return f"Pago #{self.id} - {self.estado}"


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