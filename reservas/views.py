from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .models import Producto
from .serializers import ReservaInputSerializer, ReservaOutputSerializer
from .services import ReservaService


class CrearReservaView(APIView):
    def post(self, request):
        entrada = ReservaInputSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data

        producto = get_object_or_404(Producto, id=datos["producto_id"])
        usuario = get_object_or_404(get_user_model(), id=datos["usuario_id"])

        service = ReservaService()
        try:
            reserva = service.crear_reserva({
                "usuario": usuario,
                "producto": producto,
                "fecha_limite": datos["fecha_limite"],
                "monto_anticipo": datos["monto_anticipo"],
            })
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except ValidationError as e:
            return Response({"error": e.message_dict}, status=status.HTTP_400_BAD_REQUEST)

        salida = ReservaOutputSerializer(reserva)
        return Response(salida.data, status=status.HTTP_201_CREATED)