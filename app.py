from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import db
from database.metodos import registro_bp, bp_tragamodedas, bp_ruleta, bp_deposito, bp_snake_resultado, bp_cuenta, bp_retira
from database.models import Usuario, CuentaBancaria
from database import models
from database.models import Usuario
from werkzeug.security import generate_password_hash
import os
import pymysql
pymysql.install_as_MySQLdb()

# Crear la app y configuración
app = Flask(__name__)
app.secret_key = 'clave_secreta'

# Configuración para conectar con MySQL usando PyMySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://fnafbeta:Fnaf123!@localhost/fnafbet'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



@app.route('/')
def home():
    return render_template('index.html')

#@app.route('/process', methods=['POST'])
#def process():

@app.route('/index2', methods=['GET', 'POST'])
def index2():
    return render_template('index2.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    return render_template('registro.html')

@app.route('/principal')
def principal():
    if 'usuario_id' not in session:
        return redirect(url_for('index2'))
    return render_template('principal.html')

@app.route('/terminos')
def terminos():
    if 'usuario_id' not in session:
        return redirect(url_for('index2'))
    return render_template('terminos.html')

@app.route('/menujuegos')
def menujuegos():
    if 'usuario_id' not in session:
        return redirect(url_for('index2'))
    return render_template('juegos/menujuegos.html')

@app.route('/ruleta')
def ruleta():
    if 'usuario_id' not in session:
        return redirect(url_for('index2'))
    return render_template('juegos/ruleta.html')

@app.route('/snake')
def snake():
    return render_template('juegos/snake.html')

@app.route('/tragamonedas', methods=['GET', 'POST'])
def tragamonedas():
    if 'usuario_id' not in session:
        return redirect(url_for('index2'))
    saldo = 0.0
    if 'usuario_id' in session:
        usuario = Usuario.query.get(session['usuario_id'])
        if usuario and usuario.dinero is not None:
            saldo = float(usuario.dinero)
    return render_template('juegos/tragamonedas.html', saldo=saldo)

@app.route('/tresenraya')
def tresenraya():
    if 'usuario_id' not in session:
        return redirect(url_for('index2'))
    return render_template('juegos/tresenraya.html')

@app.route("/Depositar", methods=['GET', 'POST'])
def Depositar():
    if 'usuario_id' not in session:
        return redirect(url_for('index2'))
    return render_template('depositar/Depositar.html')

@app.route("/retirar", methods=['GET', 'POST'])
def retirar():
    if 'usuario_id' not in session:
        return redirect(url_for('index2'))
    usuario_id = session['usuario_id']
    cuentas = CuentaBancaria.query.filter_by(id_usuario=usuario_id).all()
    return render_template('depositar/retirar.html', cuentas=cuentas)

@app.route("/Cuenta_bancaria", methods=['GET', 'POST'])
def Cuenta_bancaria():
    if 'usuario_id' not in session:
        return redirect(url_for('index2'))
    return render_template('depositar/Cuenta_Bancaria.html')

# Inicializar db con la app creada
db.init_app(app)

app.register_blueprint(registro_bp)
app.register_blueprint(bp_tragamodedas) 
app.register_blueprint(bp_ruleta)
app.register_blueprint(bp_deposito)
app.register_blueprint(bp_snake_resultado)
app.register_blueprint(bp_cuenta)
app.register_blueprint(bp_retira)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

