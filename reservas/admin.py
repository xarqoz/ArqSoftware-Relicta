from django.contrib import admin
from .models import Producto, Reserva


# Register your models here.

admin.site.register(Producto)
admin.site.register(Reserva)