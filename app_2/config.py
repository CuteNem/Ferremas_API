import os
from dotenv import load_dotenv

load_dotenv()
class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:SE212511374@localhost:3307/bdpythonapi'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PAYPAL_MODE = 'sandbox'  # 'live' para producción
    PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
    PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')

