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
    #valor_r = db.relationship('h_precio', backref='producto', lazy=True)
    inventario_producto_sucursal = db.relationship('Inventario', backref='producto', lazy=True)

class Sucursal(db.Model):
    id_suc = db.Column(db.Integer, primary_key=True)
    nombre_suc = db.Column(db.String(100), nullable=False)
    ubicacion = db.Column(db.String(200), nullable=False)
    inventario_productos = db.relationship('Inventario', backref='sucursal', lazy=True)

class Estado(db.Model):
    id_estado = db.Column(db.Integer, primary_key=True)
    tipo_estado = db.Column(db.String(100), nullable=False)
    
class H_precio(db.Model):
    id_precio = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    precio = db.Column(db.Integer, nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id_prod'), nullable=False) 

class Inventario(db.Model):
    id_inv = db.Column(db.Integer, primary_key=True)
    stock = db.Column(db.Integer, nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id_prod'), nullable=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id_suc'), nullable=False)   

class Consulta(db.Model):
    id_consulta = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.rut_cli'), nullable=False)
    vendedor_id = db.Column(db.Integer, db.ForeignKey('vendedor.id_vend'), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    tiempo_de_consulta = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Respuesta(db.Model):
    id_respuesta = db.Column(db.Integer, primary_key=True)
    consulta_id = db.Column(db.Integer, db.ForeignKey('consulta.id_consulta'), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    tiempo_de_respuesta = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Vendedor(db.Model):
    id_vend = db.Column(db.Integer, primary_key=True)
    nombre_vend = db.Column(db.String(100), nullable=False)
    correo_vend = db.Column(db.String(150), nullable=False, unique=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria_pdt.id_cat'), nullable=False)
    contra_vend = db.Column(db.String(100),nullable=False)

class Cliente(db.Model):
    rut_cli = db.Column(db.Integer, primary_key=True)
    nombre_cli = db.Column(db.String(100), nullable=False)
    correo_cli = db.Column(db.String(150), nullable=False, unique=True)
    contra_cli = db.Column(db.String(500), nullable=False)



#class Detalle_boleta(db.Model):
