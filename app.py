#Trabajo en la app de Flask
#Programación avanzada "A"

#Poner nombres xd:
# jhon
# jeffrey Renan Castro Velez
# pincai
# megan 


# Librerías necesarias de flask y SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import db
import pymysql

# Importar los blueprints de los métodos y los modelos de la base de datos
from database.metodos import registro_bp, bp_tragamodedas, bp_ruleta, bp_deposito, bp_snake_resultado, bp_cuenta, bp_retira, estadisticas_bp
from database.models import Usuario, CuentaBancaria



pymysql.install_as_MySQLdb()

# Crear la app y configuración
app = Flask(__name__)
app.secret_key = 'clave_secreta'

# Configuración para conectar con MySQL usando PyMySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://fnafbeta:Fnaf123!@localhost/fnafbet'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



#inializar las rutas de los html pa que se puedan ver en flask

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/index2', methods=['GET', 'POST'])
def index2():
    return render_template('index2.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    return render_template('registro.html')

@app.route('/principal')
def principal():
    #El usuario_id se guarda en la session cuando el usuario inicia sesión
    #y se elimina cuando cierra sesión
    #Si no hay usuario_id en la session, redirige a la página de inicio de sesión
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

@app.route("/estadisticas_mostrar", methods=['GET', 'POST'])
def estadisticas_mostrar():
    if 'usuario_id' not in session:
        return redirect(url_for('index2'))
    data = {}
    tipo = request.form.get('tipo')
    alcance = request.form.get('alcance')
    return render_template('estadisticas.html', data=data, tipo=tipo, alcance=alcance)
    

# Inicializar db con la app creada
db.init_app(app)

# Registrar los blueprints (los metodos para la base de datos)
app.register_blueprint(registro_bp)
app.register_blueprint(bp_tragamodedas) 
app.register_blueprint(bp_ruleta)
app.register_blueprint(bp_deposito)
app.register_blueprint(bp_snake_resultado)
app.register_blueprint(bp_cuenta)
app.register_blueprint(bp_retira)
app.register_blueprint(estadisticas_bp)

# inializar el proyecto
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

