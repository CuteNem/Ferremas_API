from flask import Flask, jsonify, request
from database.db import Config
from models import db, Categoria_pdt, Producto, Sucursal, Estado, H_precio, Inventario
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

#@app.before_first_request
#def create_tables():
#    db.create_all()

with app.app_context():
    db.create_all()

@app.route('/categorias', methods=['GET'])
def obtener_categorias():
    categorias = Categoria_pdt.query.all()
    return jsonify([{"id": Categoria_pdt.id_cat, "nombre": Categoria_pdt.nombre_cat} for Categoria_pdt in categorias])

@app.route('/categorias/<int:id_cat>/productos', methods=['GET'])
def obtener_productos_por_categoria(id_cat):
    categoria = Categoria_pdt.query.get_or_404(id_cat)
    return jsonify([{"id": Producto.id_prod, "nombre": Producto.nombre_prod, "marca": Producto.marca, "valor": Producto.valor, "categoria": Producto.categoria_id, "estado": Producto.estado_id} for Producto in categoria.productos])

@app.route('/productos', methods=['POST'])
def agregar_producto():
    nuevo_producto_data = request.json
    nuevo_producto = Producto(
        id_prod=nuevo_producto_data['id_prod'],
        nombre_prod=nuevo_producto_data['nombre_prod'],
        categoria_id=nuevo_producto_data['categoria_id']
    )
    db.session.add(nuevo_producto)
    db.session.commit()
    return jsonify({"mensaje": "Nuevo producto añadido de forma exitosa"}), 201

#OBTENER PRODUCTOS EN PROMOCION
@app.route('/promociones', methods=['GET'])
def obtener_promos():
    promociones = Producto.query.filter_by(estado_id=1).all()
    return jsonify([{"id": Producto.id_prod, "nombre": Producto.nombre_prod, "marca": Producto.marca, "valor": Producto.valor} for Producto in promociones])

#OBTENER nuevos lanzamientos
@app.route('/nuevos_lanzamientos', methods=['GET'])
def obtener_nuevos():
    nuevo_lanzamiento = Producto.query.filter_by(estado_id=2).all()
    return jsonify([{"id": Producto.id_prod, "nombre": Producto.nombre_prod, "marca": Producto.marca, "valor": Producto.valor} for Producto in nuevo_lanzamiento])

@app.route('/productos_normales', methods=['GET'])
def obtener_normales():
    normales = Producto.query.filter_by(estado_id=3).all()
    return jsonify([{"id": Producto.id_prod, "nombre": Producto.nombre_prod, "marca": Producto.marca, "valor": Producto.valor} for Producto in normales])

@app.route('/productos/<int:id_prod>/precios', methods=['GET'])
def obtener_h_precios_producto(id_prod):
    producto = Producto.query.get_or_404(id_prod)
    precios_producto = H_precio.query.filter_by(producto_id=producto.id_prod).order_by(H_precio.fecha.desc()).all()
    return jsonify([{"precio": H_precio.precio, "fecha": H_precio.fecha} for H_precio in precios_producto])

#VER PRODUCTOS POR SUCURSAL
@app.route('/sucursales/<int:id_suc>/productos', methods=['GET'])
def obtener_productos_por_sucursal(id_suc):
    sucursal_inv = Sucursal.query.get_or_404(id_suc)
    inventario_suc = Inventario.query.filter_by(sucursal_id=sucursal_inv.id_suc).all()
    return jsonify([{"id del producto": Inventario.producto_id ,"cantidad": Inventario.stock} for Inventario in inventario_suc])








































#Mensaje de bienvenida
@app.route('/',methods=['GET'])
def index():
    return jsonify({'Mensaje':'Bienvenido a API (este es un mensaje que comprueba que la API está funcionando :3)'})

if __name__ == '__main__':
    app.run(debug=True)
