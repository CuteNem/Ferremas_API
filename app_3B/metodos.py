from flask import Flask, request, jsonify
from database.db import get_connection
from werkzeug.security import check_password_hash, generate_password_hash
from models.entities.Contacto import Contacto
from models.entities.Vendedor import Vendedor
from models.entities.Cliente import Cliente
from models.entities.Consulta import Consulta
from models.entities.Respuesta import Respuesta
import time

app = Flask(__name__)

class ClienteModel:
    @classmethod
    def crear_cuenta(cls, cliente):
        try:
            cx = get_connection()
            with cx.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO cliente (rut_cli, nombre_cli, correo_cli, contra_cli) VALUES (%s, %s, %s, %s)",
                    (cliente.rut, cliente.nombre, cliente.correo, cliente.contraseña)
                )
                affected_rows = cursor.rowcount
                cx.commit()
            cx.close()
            return affected_rows
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def login(cls, cliente):
        try:
            cx = get_connection()
            with cx.cursor() as cursor:
                cursor.execute("SELECT contra_cli FROM cliente WHERE correo_cli=%s", (cliente.correo,))
                resultset = cursor.fetchone()
                if resultset is not None:
                    if check_password_hash(resultset[0], cliente.contraseña):
                        return True
                    else:
                        raise Exception("Correo o contraseña incorrecta")
                else:
                    raise Exception("Correo o contraseña incorrecta")
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def enviar_consulta(cls, consulta):
        try:
            hora_actual = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            cx = get_connection()
            with cx.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO consulta (fecha_consult, descripcion, rut_cli, id_vend) VALUES (%s, %s, %s, %s)",
                    (hora_actual, consulta.descripcion, consulta.rut_cli, consulta.id_vend)
                )
                affected_rows = cursor.rowcount
                cx.commit()
            cx.close()
            return affected_rows
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def ver_consultas(cls, rut_cli):
        try:
            cx = get_connection()
            respuesta = []
            with cx.cursor() as cursor:
                cursor.execute(
                    "SELECT id_consult, fecha_consult, descripcion, rut_cli, id_vend FROM consulta WHERE rut_cli = %s ORDER BY fecha_consult DESC", 
                    (rut_cli,)
                )
                resultset = cursor.fetchall()
                for row in resultset:
                    res = Consulta(row[0], row[1], row[2], row[3], row[4])
                    respuesta.append(res.to_JSON())
            cx.close()
            return respuesta
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def responder_consulta(cls, respuesta):
        try:
            tiempo_actual = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            cx = get_connection()
            with cx.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO respuesta (consulta_id, mensaje, tiempo_de_respuesta, id_vend) VALUES (%s, %s, %s, %s)",
                    (respuesta.consulta_id, respuesta.mensaje, tiempo_actual, respuesta.id_vend)
                )
                affected_rows = cursor.rowcount
                cx.commit()
            cx.close()
            return affected_rows
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def ver_respuestas(cls, consulta_id):
        try:
            cx = get_connection()
            respuesta = []
            with cx.cursor() as cursor:
                cursor.execute(
                    "SELECT id_respuesta, consulta_id, mensaje, tiempo_de_respuesta, id_vend FROM respuesta WHERE consulta_id = %s ORDER BY tiempo_de_respuesta DESC", 
                    (consulta_id,)
                )
                resultset = cursor.fetchall()
                for row in resultset:
                    res = Respuesta(row[0], row[1], row[2], row[3], row[4])
                    respuesta.append(res.to_JSON())
            cx.close()
            return respuesta
        except Exception as ex:
            raise Exception(ex)

# Rutas de la API
@app.route('/api/crear_cuenta', methods=['POST'])
def crear_cuenta():
    try:
        data = request.json
        cliente = Cliente(data['rut'], data['nombre'], data['correo'], generate_password_hash(data['contraseña']))
        affected_rows = ClienteModel.crear_cuenta(cliente)
        if affected_rows == 1:
            return jsonify({'message': 'Cuenta creada exitosamente'}), 201
        return jsonify({'message': 'Error al crear la cuenta'}), 500
    except Exception as ex:
        return jsonify({'message': str(ex)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        cliente = Cliente(None, None, data['correo'], data['contraseña'])
        if ClienteModel.login(cliente):
            return jsonify({'message': 'Inicio de sesión exitoso'}), 200
        return jsonify({'message': 'Correo o contraseña incorrecta'}), 401
    except Exception as ex:
        return jsonify({'message': str(ex)}), 500

@app.route('/api/enviar_consulta', methods=['POST'])
def enviar_consulta():
    try:
        data = request.json
        consulta = Consulta(None, None, data['descripcion'], data['rut_cli'], data['id_vend'])
        affected_rows = ClienteModel.enviar_consulta(consulta)
        if affected_rows == 1:
            return jsonify({'message': 'Consulta enviada exitosamente'}), 201
        return jsonify({'message': 'Error al enviar la consulta'}), 500
    except Exception as ex:
        return jsonify({'message': str(ex)}), 500

@app.route('/api/ver_consultas/<rut_cli>', methods=['GET'])
def ver_consultas(rut_cli):
    try:
        consultas = ClienteModel.ver_consultas(rut_cli)
        return jsonify(consultas), 200
    except Exception as ex:
        return jsonify({'message': str(ex)}), 500

@app.route('/api/responder_consulta', methods=['POST'])
def responder_consulta():
    try:
        data = request.json
        respuesta = Respuesta(None, data['consulta_id'], data['mensaje'], None, data['id_vend'])
        affected_rows = ClienteModel.responder_consulta(respuesta)
        if affected_rows == 1:
            return jsonify({'message': 'Respuesta enviada exitosamente'}), 201
        return jsonify({'message': 'Error al enviar la respuesta'}), 500
    except Exception as ex:
        return jsonify({'message': str(ex)}), 500

@app.route('/api/ver_respuestas/<consulta_id>', methods=['GET'])
def ver_respuestas(consulta_id):
    try:
        respuestas = ClienteModel.ver_respuestas(consulta_id)
        return jsonify(respuestas), 200
    except Exception as ex:
        return jsonify({'message': str(ex)}), 500

if __name__ == '__main__':
    app.run(debug=True)
