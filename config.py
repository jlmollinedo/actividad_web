import os

class Config:
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://appuser:Fuentepiedra.2025@192.168.4.58/actividades_extraescolares'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@localhost/actividades_extraescolares'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'jlmollinedo@gmail.com'
    MAIL_PASSWORD = 'blzs levu hzak vbbt'
    MAIL_DEFAULT_SENDER = 'jlmollinedo@gmail.com'