from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model

from reservas.models import Producto
from reservas.services import ReservaService


@method_decorator(csrf_exempt, name="dispatch")
class CrearReservaView(View):
    def post(self, request):
        producto = get_object_or_404(Producto, id=request.POST["producto_id"])
        usuario = get_object_or_404(get_user_model(), id=request.POST["usuario_id"])

        service = ReservaService()
        try:
            reserva = service.crear_reserva({
                "usuario": usuario,
                "producto": producto,
                "fecha_limite": request.POST["fecha_limite"],
                "monto_anticipo": request.POST["monto_anticipo"],
            })
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)

        return JsonResponse({"id": reserva.id, "estado": reserva.estado})