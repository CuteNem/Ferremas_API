from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Categoria_pdt(db.Model):
    id_cat = db.Column(db.Integer, primary_key=True)
    nombre_cat = db.Column(db.String(50), nullable=False)
    productos = db.relationship('Producto', backref='categoria_pdt', lazy=True)

class Producto(db.Model):
    id_prod = db.Column(db.Integer, primary_key=True)
    nombre_prod = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Integer, nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria_pdt.id_cat'), nullable=False)
    #sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id_suc'), nullable=False)
    estado_id = db.Column(db.Integer, db.ForeignKey('estado.id_estado'), nullable=False)

class Sucursal(db.Model):
    id_suc = db.Column(db.Integer, primary_key=True)
    nombre_suc = db.Column(db.String(100), nullable=False)
    ubicacion = db.Column(db.String(200), nullable=False)

class Estado(db.Model):
    id_estado = db.Column(db.Integer, primary_key=True)
    tipo_estado = db.Column(db.String(100), nullable=False)
    