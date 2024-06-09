from flask import Flask, jsonify, request
from database.db import Config
from models import db, Categoria_pdt, Producto, Sucursal, Estado

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/categorias', methods=['GET'])
def obtener_categorias():
    categorias = Categoria_pdt.query.all()
    return jsonify([{"id": Categoria_pdt.id_cat, "nombre": Categoria_pdt.nombre_cat} for Categoria_pdt in categorias])

@app.route('/categorias/<int:id_cat>/productos', methods=['GET'])
def obtener_productos_por_categoria(id_cat):
    categoria = Categoria_pdt.query.get_or_404(id_cat)
    return jsonify([{"id": Producto.id_prod, "nombre": Producto.nombre_prod, "marca": Producto.marca, "valor": Producto.valor} for Producto in Categoria_pdt.productos])


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

if __name__ == '__main__':
    app.run(debug=True)
