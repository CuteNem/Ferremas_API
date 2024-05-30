from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:neozorwave010103@localhost:3307/bdpythonapi'
app.config['SQLALCHEMY_TRACK_NOTIFICATIONS']= False

db= SQLAlchemy(app)
ma= Marshmallow(app)

class Categoria(db.Model):
    cat_id = db.Column(db.Integer,primary_key=True)
    cat_nom = db.Column(db.String(100))
    cat_desp = db.Column(db.String(100))
    
    def  __init__(self,cat_nom,cat_desp):
        self.cat_nom=cat_nom
        self.cat_desp=cat_desp

# Crear las tablas dentro del contexto de la aplicación
with app.app_context():
    db.create_all()

#Mensaje de bienvenida
@app.route('/',methods=['GET'])
def index():
    return jsonify({'Mensaje':'Bienvenido, hola! prueba11'})

if __name__=="__main__":
    app.run(debug=True)