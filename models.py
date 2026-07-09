
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(20), default='admin')

class Vianda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    disponible = db.Column(db.Boolean, default=True)
    foto = db.Column(db.String(200))

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(200))
    observaciones = db.Column(db.Text)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    fecha = db.Column(db.DateTime, default=datetime.now)
    total = db.Column(db.Float, default=0.0)
    metodo_pago = db.Column(db.String(50)) # Efectivo, Transferencia, Tarjeta
    estado = db.Column(db.String(50), default='Pendiente') # Pendiente, Preparacion, Entregado, Cancelado

class MovimientoDinero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10)) # Ingreso / Egreso
    categoria = db.Column(db.String(50))
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.now)
    descripcion = db.Column(db.String(200))
