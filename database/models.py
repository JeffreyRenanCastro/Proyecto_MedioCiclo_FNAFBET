from database import db
from datetime import datetime

# Definición de los modelos de la base de datos
# no modificar el nombre de las tablas, ya que se usan en el resto del código
# solo tocar si quieren otra tabla más

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    nombre1 = db.Column(db.String(50), nullable=False)
    nombre2 = db.Column(db.String(50))
    apellido1 = db.Column(db.String(50), nullable=False)
    apellido2 = db.Column(db.String(50))
    contraseña = db.Column(db.String(100), nullable=False)
    dinero = db.Column(db.Float, default=500)

class ResultadosSnake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    puntuacion = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

class ResultadosTragaperras(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    resultado1 = db.Column(db.String(20), nullable=False)
    resultado2 = db.Column(db.String(20), nullable=False)
    resultado3 = db.Column(db.String(20), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    dinero_invertido = db.Column(db.Float, nullable=False)
    dinero_ganado = db.Column(db.Float)

class ResultadosRuleta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    resultado = db.Column(db.String(20), nullable=False)
    apuesta = db.Column(db.String(20), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    dinero_invertido = db.Column(db.Float, nullable=False)
    dinero_ganado = db.Column(db.Float)
    
class ResultadosBlackjack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    cartas_jugador = db.Column(db.String(100))
    cartas_crupier = db.Column(db.String(100))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    dinero_invertido = db.Column(db.Float)
    dinero_ganado = db.Column(db.Float)

class RegistroBancario(db.Model):
    __tablename__ = 'registro_bancario'
    
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    titular = db.Column(db.String(100), nullable=False)  
    numero_tarjeta = db.Column(db.String(20), nullable=False)
    mes_expiracion = db.Column(db.String(2), nullable=False)
    anio_expiracion = db.Column(db.String(4), nullable=False)
    codigo_seguridad = db.Column(db.String(3), nullable=False)

class Deposito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    id_cuenta = db.Column(db.Integer, db.ForeignKey('registro_bancario.id'), nullable=False)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)
    cantidad = db.Column(db.Float, nullable=False)

class retirar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    id_cuenta = db.Column(db.Integer, db.ForeignKey('registro_bancario.id'), nullable=False)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)
    cantidad = db.Column(db.Float, nullable=False)
    
    
def getdb():
    return db