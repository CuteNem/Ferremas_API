from flask import Flask, jsonify, request, render_template
from database.db import Config
from models import db, Categoria_pdt, Producto, Sucursal, Estado, H_precio, Inventario, Vendedor, Cliente, Consulta, Respuesta
from flask_cors import CORS
from flask_jwt_extended import create_access_token
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from flask_jwt_extended import JWTManager, jwt_required
import paypalrestsdk
import requests

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
app.config["JWT_SECRET_KEY"] = "a"
jwt = JWTManager(app)

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
    categoria = Categoria_pdt.query.get(id_cat)
    if not categoria:
        return jsonify({'error': 'Este categoria no existe/no posee productos'}), 404
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
    producto = Producto.query.get(id_prod)
    if not producto:
        return jsonify({'error': 'Este producto no existe/no posee un historial de precios'}), 404
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
@app.route('/hacer_consulta', methods=['POST'])
def hacer_consulta():
    data = request.json
    pregunta = Consulta(cliente_id=data['cliente_id'], vendedor_id=data['vendedor_id'], mensaje=data['mensaje'])
    db.session.add(pregunta)
    db.session.commit()
    return jsonify({'mensaje': 'Consulta creada correctamente'}), 201


@app.route('/consulta/responder_consultas', methods=['POST'])
def escribir_respuesta(id_consulta):
    consulta = Consulta.query.get(id_consulta)
    if consulta:
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

#paypal

# Configurar PayPal SDK
paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": "AQF5Gi7NLLMsmFjU1mdLkVhFoipb4jPkNY_suDK_ix9xUFPAPUBvxPzrHqhiZuwT8yhk0aJ26tQfLlfL",
    "client_secret": "EOrH5inBlT40gTy1AraitdpbwTAfUa5_W0dMuyxrFLVCdvbwfFeYBznL3livKUyAcwtSsHKruJlC1IM8"
})

# Página principal para el pago
@app.route('/pay')
def index_pay():
    return render_template('paypal_form.html')

def obtener_tipo_de_cambio():
    try:
        url = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx?user=benjaminandrespokemon@gmail.com&pass=S212511374&firstdate=2024-06-09&timeseries=F073.TCO.PRE.Z.D&function=GetSeries"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            series = data.get('Series')
            if series:
                obs = series.get('Obs')
                if obs:
                    tipo_de_cambio = float(obs[0].get('value')) 
                    return tipo_de_cambio
        return None
    except Exception as ex:
        print("Error al obtener el tipo de cambio:", ex)
        return None

def convertir_a_dolares(valor_producto):
    try:
        tipo_de_cambio = obtener_tipo_de_cambio()
        if tipo_de_cambio is not None:
            valor_en_dolares = float(valor_producto) / tipo_de_cambio
            valor_en_dolares_redondeado = round(valor_en_dolares, 2)
            return valor_en_dolares_redondeado
        else:
            print("No se pudo obtener el tipo de cambio.")
            return None
    except Exception as ex:
        print("Error al convertir a dólares:", ex)
        return None

# Ruta para pagos desde Postman
@app.route('/payment/', methods=['POST'])
@jwt_required()
def paymentt():
    try:
        data = request.json
        producto = data.get('producto')
        valor_producto_clp = float(producto.get('valor'))
        valor_producto_usd = convertir_a_dolares(valor_producto_clp)
        if valor_producto_usd is None:
            return jsonify({"error": "No se pudo convertir el valor del producto a dólares."}), 500

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": "http://127.0.0.1:5000/execute",
                "cancel_url": "http://127.0.0.1:5000/cancel"},
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": producto.get('nombre'),
                        "sku": producto.get('id'),
                        "price": valor_producto_usd,
                        "currency": "USD",
                        "quantity": producto.get('cantidad')
                    }]
                },
                "amount": {
                    "total": valor_producto_usd * producto.get('cantidad'),
                    "currency": "USD"
                }
            }]
        })

        if payment.create():
            global datos_producto
            datos_producto = producto
            return jsonify({'paymentID': payment.id, 'USD a pagar': valor_producto_usd * producto.get('cantidad')})
        else:
            return jsonify({"error": payment.error}), 500
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500

# Variable global para almacenar datos del producto
datos_producto = {}

# Ruta para pagos desde la web
@app.route('/payment', methods=['POST'])
def payment():
    try:
        global datos_producto
        producto = datos_producto
        precio = producto.get('valor')
        valor_producto_usd = convertir_a_dolares(precio)
        
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": "http://127.0.0.1:5000/execute",
                "cancel_url": "http://127.0.0.1:5000/cancel"},
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": producto.get('nombre'),
                        "sku": producto.get('id'),
                        "price": valor_producto_usd,
                        "currency": "USD",
                        "quantity": producto.get('cantidad')
                    }]
                },
                "amount": {
                    "total": valor_producto_usd * producto.get('cantidad'),
                    "currency": "USD"
                }
            }]
        })

        if payment.create():
            return jsonify({'paymentID': payment.id})
        else:
            return jsonify({"error": payment.error}), 500
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500

# Ruta para ejecutar el pago
@app.route('/execute', methods=['POST'])
def execute():
    try:
        success = False
        data = request.json
        print("Datos recibidos en /execute:", data)
        paymentID = data.get('paymentID')
        payerID = data.get('payerID')

        payment = paypalrestsdk.Payment.find(paymentID)
        if payment.execute({'payer_id': payerID}):
            success = True
        else:
            return jsonify({"error": payment.error}), 500

        return jsonify({'success': success})
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500

## CLIENTE
@app.route('/crear_cliente', methods=['POST'])
def agregar_cliente():
    nuevo_cliente_data = request.json
    try:
        nuevo_cliente = Cliente(
            rut_cli=nuevo_cliente_data['rut_cli'],
            nombre_cli=nuevo_cliente_data['nombre_cli'],
            correo_cli=nuevo_cliente_data['correo_cli'],
            contra_cli=nuevo_cliente_data['contra_cli'])
        nuevo_cliente.contra_cli = generate_password_hash(nuevo_cliente.contra_cli)
        db.session.add(nuevo_cliente)
        db.session.commit()
        return jsonify({"mensaje": "Cuenta Creada. Inicia sesion"}), 201
    except Exception as e:
        db.session.rollback()  # Deshacer cambios en caso de error
        return jsonify({"error": str(e)}), 400

##LOGIN
@app.route('/login', methods=['POST'])
def ingresar_usuario():
    datos_ingreso = request.json
    correo_cli = datos_ingreso.get('correo_cli')
    contra_cli = datos_ingreso.get('contra_cli')
    if not correo_cli or not contra_cli:
        return jsonify({"error": "Correo y contraseña son requeridos"}), 400
    cliente = Cliente.query.filter_by(correo_cli=correo_cli).first_or_404(description="Usuario no encontrado")
    print(cliente.contra_cli)
    print(contra_cli)
    print(check_password_hash(cliente.contra_cli, contra_cli))
    if check_password_hash(cliente.contra_cli, contra_cli):
        acces_token = create_access_token(identity=correo_cli)
        return jsonify({"mensaje": "Inicio de sesión exitoso", "token": acces_token, "user_id": correo_cli}), 200
    else:
        return jsonify({"error": "Correo o contraseña incorrecta"}), 400


#Mensaje de bienvenida
@app.route('/',methods=['GET'])
def index():
    return jsonify({'Mensaje':'Bienvenido a API (este es un mensaje que comprueba que la API está funcionando :3)'})

if __name__ == '__main__':
    app.run(debug=True)


"""
TEST's
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