"""
Modelos del Microservicio de Pagos.
Utiliza Flask-SQLAlchemy con base de datos propia (desacoplada del monolito Django).
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Pago(db.Model):
    """
    Representa un pago asociado a una Orden del sistema.

    El microservicio NO tiene FK real a la tabla Orden de Django;
    en su lugar mantiene el `orden_id` como referencia externa (loose coupling).
    """

    __tablename__ = "pagos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    orden_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    metodo = db.Column(db.String(20), nullable=False)  # 'tarjeta' | 'transferencia'
    estado = db.Column(db.String(20), nullable=False, default="pendiente")
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    aprobado_en = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        """Serializa el modelo a un diccionario JSON-compatible."""
        return {
            "id": self.id,
            "orden_id": self.orden_id,
            "monto": float(self.monto),
            "metodo": self.metodo,
            "estado": self.estado,
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
            "aprobado_en": self.aprobado_en.isoformat() if self.aprobado_en else None,
        }

    def __repr__(self):
        return f"<Pago #{self.id} orden={self.orden_id} estado={self.estado}>"
