#Trabajo en la app de Flask
#Programación avanzada "A"

#Poner nombres xd:
# Jhon David Burgos Panta
# jeffrey Renan Castro Velez
# John Alexander Pincay Baque
# Megan Yasmina Mieles Loor


# Librerías necesarias de flask y SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import db
import pymysql
from sqlalchemy import func

# Importar los blueprints de los métodos y los modelos de la base de datos
from database.metodos import registro_bp, bp_tragamodedas, bp_ruleta, bp_blackjack, bp_deposito, bp_snake_resultado, bp_cuenta, bp_retira, estadisticas_bp
from database.models import Usuario, CuentaBancaria, ResultadosRuleta, ResultadosBlackjack, ResultadosTragaperras, ResultadosSnake



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
    if 'usuario_id' in session:
        return redirect(url_for('principal'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'usuario_id' in session:
        return redirect(url_for('principal'))
    return render_template('auth/login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if 'usuario_id' in session:
        return redirect(url_for('principal'))
    return render_template('auth/registro.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente.', 'success')
    return redirect(url_for('home'))



@app.route('/principal')
def principal():
    #El usuario_id se guarda en la session cuando el usuario inicia sesión
    #y se elimina cuando cierra sesión
    #Si no hay usuario_id en la session, redirige a la página de inicio de sesión
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    usuario = Usuario.query.get(session['usuario_id'])
    return render_template('principal.html', usuario=usuario)

@app.route('/terminos')
def terminos():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    return render_template('others/terminos.html')

@app.route('/menujuegos')
def menujuegos():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    usuario = Usuario.query.get(session['usuario_id'])
    return render_template('games/menujuegos.html', usuario=usuario)

@app.route('/ruleta')
def ruleta():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    usuario = db.session.get(Usuario, session['usuario_id'])
    return render_template('games/ruleta.html', usuario=usuario)

@app.route('/blackjack' , methods=['GET', 'POST'])
def blackjack():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    usuario = db.session.get(Usuario, session['usuario_id'])
    return render_template('games/blackjack.html', usuario=usuario)

@app.route('/snake')
def snake():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    usuario = db.session.get(Usuario, session['usuario_id'])
    return render_template('games/snake.html', usuario=usuario)

@app.route('/tragamonedas', methods=['GET', 'POST'])
def tragamonedas():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    saldo = 0.0
    if 'usuario_id' in session:
        usuario = Usuario.query.get(session['usuario_id'])
        if usuario and usuario.dinero is not None:
            saldo = float(usuario.dinero)
    return render_template('games/tragamonedas.html', saldo=saldo , usuario=usuario)

@app.route('/tresenraya')
def tresenraya():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    usuario =Usuario.query.get(session['usuario_id'])
    return render_template('games/tresenraya.html', usuario=usuario)

@app.route("/Depositar", methods=['GET', 'POST'])
def Depositar():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    return render_template('transactions/depositar.html')

@app.route("/retirar", methods=['GET', 'POST'])
def retirar():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    usuario_id = session['usuario_id']
    cuentas = CuentaBancaria.query.filter_by(id_usuario=usuario_id).all()
    return render_template('transactions/retirar.html', cuentas=cuentas)

@app.route("/Cuenta_bancaria", methods=['GET', 'POST'])
def Cuenta_bancaria():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    return render_template('cuenta/cuenta_bancaria.html')

@app.route("/estadisticas_mostrar", methods=['GET', 'POST'])
def estadisticas_mostrar():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    usuario = Usuario.query.get(session['usuario_id'])
    tipo = request.form.get('tipo', 'ruleta')  # por defecto ruleta
    alcance = request.form.get('alcance', 'global')  # por defecto global
    data = {}

    if tipo == 'ruleta':
        query = ResultadosRuleta.query
        if alcance == 'propias':
            query = query.filter_by(id_usuario=usuario.id)
        resultados = query.all()
        for r in resultados:
            clave = r.resultado
            data[clave] = data.get(clave, 0) + 1
            
    elif tipo == 'blackjack':
        query = ResultadosBlackjack.query    
        if alcance == 'propias':
            query = query.filter_by(id_usuario=usuario.id)
        resultados = query.all()
        for r in resultados:
            if r.dinero_ganado > r.dinero_invertido:
                clave = "Ganó"
            elif r.dinero_ganado < r.dinero_invertido:
                clave = "Perdió"
            else:
                clave = "Empate"
            data[clave] = data.get(clave, 0) + 1  

    elif tipo == 'tragaperras':
        query = ResultadosTragaperras.query
        if alcance == 'propias':
            query = query.filter_by(id_usuario=usuario.id)
        resultados = query.all()
        for r in resultados:
            clave = f"{r.resultado1}-{r.resultado2}-{r.resultado3}"
            data[clave] = data.get(clave, 0) + 1

    elif tipo == 'snake':
        query = ResultadosSnake.query
        if alcance == 'propias':
            query = query.filter_by(id_usuario=usuario.id)
        resultados = query.all()
        for r in resultados:
            puntos = str(r.puntuacion)
            data[puntos] = data.get(puntos, 0) + 1

    return render_template("statistics/estadisticas.html", usuario=usuario, data=data, tipo=tipo, alcance=alcance)
    

# Inicializar db con la app creada
db.init_app(app)

# Registrar los blueprints (los metodos para la base de datos)
app.register_blueprint(registro_bp)
app.register_blueprint(bp_tragamodedas) 
app.register_blueprint(bp_ruleta)
app.register_blueprint(bp_blackjack)
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

