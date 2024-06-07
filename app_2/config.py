import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:rootpass123@localhost:3307/bdtestpythonapi'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PAYPAL_MODE = 'sandbox'  # 'live' para producción
    PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
    PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')

