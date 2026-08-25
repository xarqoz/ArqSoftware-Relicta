from rest_framework import serializers
from .models import Reserva, Producto


class ReservaInputSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField()
    usuario_id = serializers.IntegerField()
    fecha_limite = serializers.DateField()
    monto_anticipo = serializers.DecimalField(max_digits=10, decimal_places=2)


class ReservaOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = ["id", "producto", "usuario", "fecha_limite", "monto_anticipo", "estado", "creada_en"]