from app import db
from models import *

with db.app.app_context():
    db.create_all()
    print("Base de datos inicializada correctamente.")
