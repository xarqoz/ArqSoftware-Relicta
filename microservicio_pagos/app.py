"""
Microservicio de Pagos - Flask
Strangler Pattern: extrae el procesamiento de pagos del monolito Django.

Responsabilidades:
- Recibir una solicitud de pago para una Orden
- Validar campos y montos
- Registrar el pago en su propia base de datos
- Retornar estado del pago con estructura JSON estandarizada
"""

import os
from flask import Flask, request, jsonify
from models import db, Pago
from datetime import datetime

app = Flask(__name__)

# ── Configuración de Base de Datos ────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///pagos.db")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# ── Helpers ───────────────────────────────────────────────────────────────────

def error_response(mensaje, codigo):
    """Respuesta de error estandarizada (400/404/409/500)."""
    return jsonify({"error": mensaje, "status": codigo}), codigo


def success_response(data, codigo=200):
    """Respuesta de éxito estandarizada."""
    return jsonify({"data": data, "status": codigo}), codigo


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    """Health-check para Docker y Nginx."""
    return jsonify({"status": "ok", "servicio": "pagos", "timestamp": datetime.utcnow().isoformat()}), 200


@app.route("/api/v2/pagos/", methods=["POST"])
def procesar_pago():
    """
    Procesa un nuevo pago para una orden.

    Body JSON esperado:
    {
        "orden_id": <int>,
        "monto":    <float>,
        "metodo":   "tarjeta" | "transferencia"
    }

    Respuestas:
    - 201: Pago creado y en estado 'pendiente'
    - 400: Campos faltantes o inválidos
    - 409: Ya existe un pago para esa orden
    - 500: Error interno del servidor
    """
    if not request.is_json:
        return error_response("El Content-Type debe ser application/json", 400)

    data = request.get_json()

    # ── Validación de campos requeridos ──────────────────────────────────────
    campos_requeridos = ["orden_id", "monto", "metodo"]
    faltantes = [c for c in campos_requeridos if c not in data]
    if faltantes:
        return error_response(f"Campos requeridos faltantes: {', '.join(faltantes)}", 400)

    # ── Validación de tipos y valores ────────────────────────────────────────
    try:
        orden_id = int(data["orden_id"])
        monto = float(data["monto"])
    except (ValueError, TypeError):
        return error_response("orden_id debe ser entero y monto debe ser numérico", 400)

    if monto <= 0:
        return error_response("El monto debe ser mayor a 0", 400)

    metodo = data["metodo"]
    METODOS_VALIDOS = {"tarjeta", "transferencia"}
    if metodo not in METODOS_VALIDOS:
        return error_response(f"Método inválido. Valores aceptados: {', '.join(METODOS_VALIDOS)}", 400)

    # ── Verificar pago duplicado ──────────────────────────────────────────────
    pago_existente = Pago.query.filter_by(orden_id=orden_id).first()
    if pago_existente:
        return error_response(f"Ya existe un pago para la orden #{orden_id}", 409)

    # ── Crear pago ────────────────────────────────────────────────────────────
    try:
        nuevo_pago = Pago(
            orden_id=orden_id,
            monto=monto,
            metodo=metodo,
            estado="pendiente",
        )
        db.session.add(nuevo_pago)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error al registrar el pago: {str(e)}", 500)

    return success_response(nuevo_pago.to_dict(), 201)


@app.route("/api/v2/pagos/<int:pago_id>/aprobar/", methods=["PATCH"])
def aprobar_pago(pago_id):
    """
    Aprueba un pago que se encuentre en estado 'pendiente'.

    Respuestas:
    - 200: Pago aprobado exitosamente
    - 404: Pago no encontrado
    - 409: El pago no está en estado 'pendiente'
    - 500: Error interno del servidor
    """
    pago = Pago.query.get(pago_id)
    if not pago:
        return error_response(f"Pago #{pago_id} no encontrado", 404)

    if pago.estado != "pendiente":
        return error_response(
            f"Solo se pueden aprobar pagos en estado 'pendiente'. Estado actual: '{pago.estado}'",
            409,
        )

    try:
        pago.estado = "aprobado"
        pago.aprobado_en = datetime.utcnow()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error al aprobar el pago: {str(e)}", 500)

    return success_response(pago.to_dict(), 200)


@app.route("/api/v2/pagos/<int:pago_id>/", methods=["GET"])
def obtener_pago(pago_id):
    """
    Retorna el detalle de un pago por su ID.

    Respuestas:
    - 200: Detalle del pago
    - 404: Pago no encontrado
    """
    pago = Pago.query.get(pago_id)
    if not pago:
        return error_response(f"Pago #{pago_id} no encontrado", 404)

    return success_response(pago.to_dict(), 200)


@app.route("/api/v2/pagos/orden/<int:orden_id>/", methods=["GET"])
def obtener_pago_por_orden(orden_id):
    """
    Retorna el pago asociado a una orden específica.

    Respuestas:
    - 200: Detalle del pago
    - 404: No existe pago para esa orden
    """
    pago = Pago.query.filter_by(orden_id=orden_id).first()
    if not pago:
        return error_response(f"No se encontró pago para la orden #{orden_id}", 404)

    return success_response(pago.to_dict(), 200)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
