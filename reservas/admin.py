from django.contrib import admin
from .models import Producto, Reserva, Categoria, Orden, OrdenItem, Pago

admin.site.register(Categoria)
admin.site.register(Producto)
admin.site.register(Orden)
admin.site.register(OrdenItem)
admin.site.register(Pago)
admin.site.register(Reserva)