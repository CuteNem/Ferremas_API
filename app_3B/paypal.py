from flask import Flask, render_template, jsonify, request, Blueprint
#from flask_jwt_extended import jwt_required, JWTManager
import paypalrestsdk
import requests

app = Flask(__name__)

"""
app.config["JWT_SECRET_KEY"] = "super-secret"  # Clave secreta para firmar los tokens JWT
jwt = JWTManager(app)
"""
paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": "AQF5Gi7NLLMsmFjU1mdLkVhFoipb4jPkNY_suDK_ix9xUFPAPUBvxPzrHqhiZuwT8yhk0aJ26tQfLlfL",
    "client_secret": "EOrH5inBlT40gTy1AraitdpbwTAfUa5_W0dMuyxrFLVCdvbwfFeYBznL3livKUyAcwtSsHKruJlC1IM8"
})

main = Blueprint('paypal', __name__)

@main.route('/')
def index():
    return render_template('paypal_form.html')

datos_producto = {}

@main.route('/payment', methods=['POST'])
def payment():
    try:
        global datos_producto
        producto = datos_producto
        nombre = producto.get('nombre')
        print(nombre)
        precio = producto.get('precio')  
        valor_producto_usd = convertir_a_dolares(precio)  
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"},
            "redirect_urls": {
                "return_url": "https://322849a8-76c0-4ca6-b4a5-0d42e602d5f2-00-2buxrp1eapygi.picard.replit.dev/paypal/payment/execute",
                "cancel_url": "https://322849a8-76c0-4ca6-b4a5-0d42e602d5f2-00-2buxrp1eapygi.picard.replit.dev/paypal/"},
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": producto.get('nombre'),
                        "sku": producto.get('codigo_prod'),
                        "price": valor_producto_usd, 
                        "currency": "USD",
                        "quantity": producto.get('cantidad'),}]},
                        "amount": {
                        "total": valor_producto_usd * producto.get('cantidad'),
                        "currency": "USD"},}]})
        if payment.create():
                print('ID de pago creada')
                return jsonify({'paymentID': payment.id})
        else:
                print(payment.error)
                return jsonify({"error": payment.error}), 50
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500

@main.route('/execute', methods=['POST'])
def execute():
        try:
            print("LLegue a execute")
            success = False
            paymentID = request.form.get('paymentID')
            payerID = request.form.get('payerID')
            global datos_producto
            producto = datos_producto
            print(producto.get('nombre'))
            if not paymentID or not payerID or not producto:
                return jsonify({"error": "Faltan datos en la solicitud"}), 400
            payment = paypalrestsdk.Payment.find(paymentID)
            if payment.execute({'payer_id': payerID}):
                    success = True
            else:
                print(payment.error)
                return jsonify({"error": payment.error}), 500

            return jsonify({'success': success})
        except Exception as ex:
            return jsonify({"error": str(ex)}), 500


    
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
                else:
                    return None
            except Exception as ex:
                print("Error al obtener el tipo de cambio:", ex)
                return None

def convertir_a_dolares(valor_producto):
            try:
                tipo_de_cambio = obtener_tipo_de_cambio()
                if tipo_de_cambio is not None:
                    valor_en_dolares = float(valor_producto) / tipo_de_cambio
                    # Redondear el valor a dos decimales
                    valor_en_dolares_redondeado = round(valor_en_dolares, 2)
                    return valor_en_dolares_redondeado
                else:
                    print("No se pudo obtener el tipo de cambio.")
                    return None
            except Exception as ex:
                print("Error al convertir a dólares:", ex)
                return None

@app.route('/payment/', methods=['POST'])
#@jwt_required() 
def paymentt():
            try:
                data = request.json
                producto = data.get('producto')
                valor_producto_clp = float(producto.get('precio'))
                print(valor_producto_clp)
                # Convertir el valor del producto de CLP a USD
                valor_producto_usd = convertir_a_dolares(valor_producto_clp)
                if valor_producto_usd is None:
                    return jsonify({"error": "No se pudo convertir el valor del producto a dólares."}), 500

                # Crear el objeto de pago de PayPal con el valor en USD
                payment = paypalrestsdk.Payment({
                    "intent": "sale",
                    "payer": {
                        "payment_method": "paypal"},
                    "redirect_urls": {
                        "return_url": "https://322849a8-76c0-4ca6-b4a5-0d42e602d5f2-00-2buxrp1eapygi.picard.replit.dev/",
                        "cancel_url": "https://322849a8-76c0-4ca6-b4a5-0d42e602d5f2-00-2buxrp1eapygi.picard.replit.dev/"
                    },
                    "transactions": [{
                        "item_list": {
                            "items": [{
                                "name": producto.get('nombre'),
                                "sku": producto.get('codigo_prod'),
                                "price": valor_producto_usd, 
                                "currency": "USD",
                                "quantity": producto.get('cantidad'),
                            }]
                        },
                        "amount": {
                            "total": valor_producto_usd * producto.get('cantidad'),
                            "currency": "USD"
                        },
                    }]
                })
                #a=ProductoModel.Saber_Stock(producto.get('codigo_prod'), producto.get('id_sucursal'))
                #print(a)
                #if a < producto.get('cantidad'):
                #    return jsonify({"message": "No hay suficiente stock"}), 500
                #else:
                if payment.create():
                        print('ID de pago creada')
                        print('Valor a cobrar en PayPal:', valor_producto_usd * producto.get('cantidad'), 'USD')
                        global datos_producto
                        datos_producto = producto
                        return jsonify({'paymentID': payment.id, 'USD a pagar': valor_producto_usd * producto.get('cantidad')})
                else:
                        return jsonify({"error": payment.error}), 500
            except Exception as ex:
                return jsonify({"error": str(ex)}), 500

if __name__ == '__main__':
    app.run(debug=True)
