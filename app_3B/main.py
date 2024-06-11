from flask import Flask, jsonify, request
from database.db import Config
from models import db, Categoria_pdt, Producto, Sucursal, Estado, H_precio, Inventario, Vendedor, Cliente, Consulta, Respuesta
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

#@app.before_first_request
#def create_tables():
#    db.create_all()

with app.app_context():
    db.create_all()

#OBTENER TODAS LAS CATEGORIAS
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

#Obtiene los productos de un estado en especifico
@app.route('/estado/<int:id_estado>/obtener_productos', methods=['GET'])
def obtener_productos_estado(id_estado):
    estado = Estado.query.get(id_estado)
    if not estado:
        return jsonify({'error': 'Este estado no existe/no posee productos'}), 404
    productos = Producto.query.filter_by(estado_id=id_estado).all()
    resultado = [{"nombre del estado": estado.tipo_estado,"id": producto.id_prod,"nombre": producto.nombre_prod,"marca": producto.marca,"valor": producto.valor}for producto in productos]
    return jsonify(resultado)


#TODOS LOS PRODUCTOS QUE TENGAN UN HISTORIAL DE PRECIOS
@app.route('/productos/<int:id_prod>/precios', methods=['GET'])
def obtener_h_precios_producto(id_prod):
    producto = Producto.query.get_or_404(id_prod)
    precios_producto = H_precio.query.filter_by(producto_id=producto.id_prod).order_by(H_precio.fecha.desc()).all()
    return jsonify([{"precio": H_precio.precio, "fecha": H_precio.fecha} for H_precio in precios_producto])

#conseguir un producto por sucursal segun su id
@app.route('/sucursales/obtener_producto/<int:id_prod>', methods=['GET'])
def obtener_producto_de_una_sucursal(id_prod):
        producto_sucursal = Producto.query.get(id_prod)
        if not producto_sucursal:
            return jsonify({'error': 'Producto no encontrado/ no existente'}), 404
        inventario_producto = db.session.query(Inventario, Sucursal, Producto).join(Sucursal, Inventario.sucursal_id == Sucursal.id_suc).join(Producto, Inventario.producto_id == Producto.id_prod).filter(Inventario.producto_id == id_prod).all()
        return jsonify([{"nombre del producto": Producto.nombre_prod ,"id del producto": Inventario.producto_id ,"nombre de la sucursal": Sucursal.nombre_suc,"cantidad": Inventario.stock} for Inventario, Sucursal, Producto in inventario_producto])

#sistema de consultas y respuestas
@app.route('/pregunta', methods=['POST'])
def hacer_consulta():
    data = request.json
    pregunta = Consulta(cliente_id=data['cliente_id'], vendedor_id=data['vendedor_id'], mensaje=data['mensaje'])
    db.session.add(pregunta)
    db.session.commit()
    return jsonify({'mensaje': 'Consulta creada correctamente'}), 201

@app.route('/pregunta/<int:id_consulta>/respuesta', methods=['POST'])
def escribir_respuesta(id_consulta):
    consulta = Consulta.query.get(id_consulta)
    if not consulta:
        return jsonify({'error': 'Consulta no encontrada'}), 404
    data = request.json
    respuesta = Respuesta(consulta_id=id_consulta, mensaje=data['mensaje'])
    db.session.add(respuesta)
    db.session.commit()
    return jsonify({'mensaje': 'Respuesta creada correctamente'}), 201


@app.route('/pregunta/<int:id_consulta>', methods=['GET'])
def ver_pregunta(id_consulta):
    consulta = Consulta.query.get(id_consulta)
    if not consulta:
        return jsonify({'error': 'Consulta no encontrada'}), 404
    respuestas = Respuesta.query.filter_by(consulta_id=id_consulta).all()
    return jsonify  ([{'id_consulta': consulta.id_consulta,'cliente_id': consulta.cliente_id,'vendedor_id': consulta.vendedor_id,
                    'mensaje': consulta.mensaje,
                    'tiempo_de_consulta': consulta.tiempo_de_consulta.strftime('%Y-%m-%d %H:%M:%S'),
                    'respuestas': [{'id_respuesta': r.id_respuesta,'mensaje': r.mensaje,'tiempo_de_respuesta': r.tiempo_de_respuesta.strftime('%Y-%m-%d %H:%M:%S')} for r in respuestas ]
                    }])





































#Mensaje de bienvenida
@app.route('/',methods=['GET'])
def index():
    return jsonify({'Mensaje':'Bienvenido a API (este es un mensaje que comprueba que la API está funcionando :3)'})

if __name__ == '__main__':
    app.run(debug=True)


"""
#TODOS LOS PRODUCTOS DEPENDIENTO DEL ID DE LA SUCURSAL
@app.route('/sucursales/<int:id_suc>/productos', methods=['GET'])
def obtener_productos_por_sucursal(id_suc):
    sucursal_inv = Sucursal.query.get_or_404(id_suc)
    inventario_suc = db.session.query(Inventario, Producto).join(Producto, Inventario.producto_id == Producto.id_prod).filter(Inventario.sucursal_id==sucursal_inv.id_suc).all()
    return jsonify([{"id del producto": Inventario.producto_id ,"nombre del producto": producto.nombre_prod,"cantidad": Inventario.stock} for Inventario, producto in inventario_suc])

#ontiene total de productos en general
@app.route('/productos_total', methods=['GET'])
def obtener_total_productos():
    #producto = Producto.query.all()
    productos = db.session.query(Producto, Estado, Categoria_pdt).join(Estado, Producto.estado_id == Estado.id_estado).join(Categoria_pdt, Producto.categoria_id == Categoria_pdt.id_cat).all()
    return jsonify([{"id": Producto.id_prod, "nombre": Producto.nombre_prod, "marca": Producto.marca, "valor": Producto.valor, "categoria": categoria.nombre_cat, "estado": estado.tipo_estado} for Producto, estado, categoria in productos])

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



""" TEST's
#TODOS LOS PRODUCTOS DEPENDIENTO DEL ID DE LA SUCURSAL
@app.route('/sucursales/<int:id_suc>/productos', methods=['GET'])
def obtener_productos_por_sucursal(id_suc):
    sucursal_inv = Sucursal.query.get(id_suc)
    if not sucursal_inv:
        return jsonify({'error': 'Sucursal no encontrada/ no existente'}), 404
    inventario_suc = db.session.query(Inventario, Producto).join(Producto, Inventario.producto_id == Producto.id_prod).filter(Inventario.sucursal_id==sucursal_inv.id_suc).all()
    return jsonify([{"id del producto": Inventario.producto_id ,"nombre del producto": producto.nombre_prod,"cantidad": Inventario.stock} for Inventario, producto in inventario_suc])

#obtener los producto dependiendo del id del estado
@app.route('/estado/<int:id_estado>/obtener_productos', methods=['GET'])
def obtener_productos_estado(id_estado):
    productos = Estado.query.get(id_estado)
    if not productos:
            return jsonify({'error': 'Este estado no existe/no posee productos'}), 404
    estado_producto = db.session.query(Estado, Producto).join(Estado, Producto.estado_id == Estado.id_estado).filter(Producto.estado_id==id_estado).all()
    return jsonify([{"nombre del estado": Estado.tipo_estado ,"id": producto.id_prod, "nombre": producto.nombre_prod, "marca": producto.marca, "valor": producto.valor} for producto in estado_producto])


#ontiene total de productos en general
@app.route('/productos_total', methods=['GET'])
def obtener_total_productos():
    #producto = Producto.query.all()
    productos = db.session.query(Producto, Estado, Categoria_pdt).join(Estado, Producto.estado_id == Estado.id_estado).join(Categoria_pdt, Producto.categoria_id == Categoria_pdt.id_cat).all()
    return jsonify([{"id": Producto.id_prod, "nombre": Producto.nombre_prod, "marca": Producto.marca, "valor": Producto.valor, "categoria": categoria.nombre_cat, "estado": estado.tipo_estado} for Producto, estado, categoria in productos])

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

#OBTENER TODOS LOS PRODUCTOS SIN PROMOCION O LANZAMIENTO RECIENTE
@app.route('/productos_normales', methods=['GET'])
def obtener_normales():
    normales = Producto.query.filter_by(estado_id=3).all()
    return jsonify([{"id": Producto.id_prod, "nombre": Producto.nombre_prod, "marca": Producto.marca, "valor": Producto.valor} for Producto in normales])
"""