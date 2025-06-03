from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from database import db
from database.models import Usuario, ResultadosTragaperras, ResultadosRuleta, ResultadosBlackjack, Deposito, ResultadosSnake, CuentaBancaria, retirar
from datetime import datetime



import random
from passlib.hash import scrypt

#Usamos este archivo para crear los metodos get y set de la base de datos
# y los metodos para guardar los resultados de los juegos


registro_bp = Blueprint('registro', __name__)

#metodo para registrar un nuevo usuario
@registro_bp.route('/registrousuario', methods=['GET', 'POST'])
def registro_usuario():
    print("Entrando a la vista de registro")
    if request.method == 'POST':
        print("Formulario recibido")
        usuario = request.form['usuario']
        nombre1 = request.form['nombre1']
        apellido1 = request.form['apellido1']
        apellido2 = request.form.get('apellido2')
        correo = request.form['correo']
        contrasenia = request.form['contrasenia']
        print("Datos recibidos:", usuario, nombre1, apellido1, apellido2, correo, contrasenia)
        if Usuario.query.filter((Usuario.usuario == usuario) | (Usuario.correo == correo)).first():
            flash('El usuario o correo ya existe.', 'error')
            return redirect(url_for('registro.registro_usuario'))
        
        nuevo_usuario = Usuario(
            usuario=usuario,
            nombre1=nombre1,
            apellido1=apellido1,
            apellido2=apellido2,
            correo=correo,            
            contraseña=scrypt.hash(contrasenia)
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Registro exitoso.', 'success')
        print("Usuario registrado:", nuevo_usuario.usuario)
        flash('Usuario registrado exitosamente.', 'success')
        flash("¡Registro exitoso! Bienvenido a FNAF.BET", "success")
        return redirect(url_for('home'))
        #return redirect(url_for('registro.registro_usuario'))

    return render_template('auth/registro.html')

#metodo para iniciar sesion
@registro_bp.route('/auth_login', methods=['GET', 'POST'])
def login_usuario():
    if request.method == 'POST':
        correo = request.form['email']
        contrasenia = request.form['password']

        # Buscar usuario por correo
        usuario = Usuario.query.filter_by(correo=correo).first()

        if not usuario:
            flash('Correo o contraseña incorrectos.', 'error')
            return redirect(url_for('registro.login_usuario'))

        print("Datos de inicio de sesión:", correo, contrasenia)
        print(f"Contraseña ingresada: {contrasenia}")
        print("Contraseña almacenada:", usuario.contraseña)

        if scrypt.verify(contrasenia, usuario.contraseña):
            # Inicio de sesión exitoso
            session['usuario_id'] = usuario.id
            session['usuario'] = usuario.usuario
            flash(f'Bienvenido, {usuario.usuario}!', 'success')
            return redirect(url_for('principal'))  # Cambia 'principal' si tu endpoint es diferente
        else:
            flash('Correo o contraseña incorrectos.', 'error')
            return redirect(url_for('registro.login_usuario'))

    return render_template('login.html')

#metodo para guardar el resultado de la tragamonedas
bp_tragamodedas = Blueprint('tragaperras_giro', __name__)
@bp_tragamodedas.route('/guardar_resultado_tragamonedas', methods=['POST'])
def guardar_resultado_tragamonedas():
    if 'usuario_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    data = request.get_json()
    resultado1 = data.get('resultado1')
    resultado2 = data.get('resultado2')
    resultado3 = data.get('resultado3')
    dinero_jugado = float(data.get('dinero_jugado', 0))
    ganado = data.get('ganado', False)

    dinero_ganado = dinero_jugado * 5 if ganado else 0

    usuario = db.session.get(Usuario, session['usuario_id'])
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Verificar saldo suficiente
    if usuario.dinero is None or usuario.dinero < dinero_jugado:
        return jsonify({"error": "Saldo insuficiente"}), 400

    # Guardar resultado
    print("Guardando resultado de tragamonedas")
    nuevo_resultado = ResultadosTragaperras(
        id_usuario=usuario.id,
        resultado1=resultado1,
        resultado2=resultado2,
        resultado3=resultado3,
        dinero_invertido=dinero_jugado,
        dinero_ganado=dinero_ganado
    )
    db.session.add(nuevo_resultado)
    print("Resultado guardado:", nuevo_resultado)
    # Actualizar saldo
    usuario.dinero -= dinero_jugado
    usuario.dinero += dinero_ganado

    db.session.commit()

    return jsonify({"saldo_actual": round(usuario.dinero, 2)}), 200

bp_ruleta = Blueprint('ruleta_juego', __name__)


#metodo para guardar el resultado de la ruleta
@bp_ruleta.route('/jugar_ruleta', methods=['POST'])
def jugar_ruleta():
    if 'usuario_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    data = request.get_json()
    tipo = data.get("tipo_apuesta")
    valor = data.get("valor_apuesta")
    dinero = data.get("dinero_apostado")

    usuario = db.session.get(Usuario, session['usuario_id'])
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    if usuario.dinero is None or usuario.dinero < dinero:
        return jsonify({"error": "Saldo insuficiente"}), 400

    # Generar número de ruleta entre 0 y 36
    resultado_numero = random.randint(0, 36)
    if resultado_numero == 0 or resultado_numero == 00:
        resultado_color = 'verde'
    elif resultado_numero in [23, 14, 9,  30, 7, 32, 5, 34, 3, 36, 1, 27 ,25, 12, 19, 18, 21, 16]: 
        resultado_color = 'rojo'
    else:
        resultado_color = 'negro'

    gano = False
    dinero_ganado = 0

    if tipo == 'color':
        if valor == resultado_color:
            gano = True
            dinero_ganado = dinero * 2  # paga 1:1
    elif tipo == 'numero':
        if int(valor) == resultado_numero:
            gano = True
            dinero_ganado = dinero * 36  # paga 35:1

    usuario.dinero -= dinero
    usuario.dinero += dinero_ganado

    resultado = ResultadosRuleta(
        id_usuario=usuario.id,
        resultado=resultado_numero,  # número que salió
        apuesta=valor,               # guardas el valor que apostó (ej: "rojo" o "5")
        dinero_invertido=dinero,
        dinero_ganado=dinero_ganado
    )
    db.session.add(resultado)
    db.session.commit()

    return jsonify({
        "resultado_numero": resultado_numero,
        "resultado_color": resultado_color,
        "gano": gano,
        "dinero_ganado": dinero_ganado,
        "saldo_actual": round(usuario.dinero, 2)
    })
    
    
bp_blackjack = Blueprint('blackjack_resultado', __name__)
#metodo para guardar el resultado de blackjack
@bp_blackjack.route('/comprobar_dinero_blackjack', methods=['POST'])
def comprobar_dinero_blackjack():
    print("aaaaaaaaaa")
    if 'usuario_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    data = request.get_json()
    
    dinero_jugado = float(data.get('dinero_jugado', 0))
    
    if dinero_jugado <= 0:
        return jsonify({"error": "La apuesta debe ser mayor que cero"}), 400

    usuario = db.session.get(Usuario, session['usuario_id'])
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    if usuario.dinero is None or usuario.dinero < dinero_jugado:
        return jsonify({"error": "Saldo insuficiente"}), 400

    return jsonify({"success": True, "saldo_actual": round(usuario.dinero, 2)})


@bp_blackjack.route('/guardar_resultado_blackjack', methods=['POST'])
def guardar_resultado_blackjack():
    print("Entrando a guardar resultado de blackjack")

    if 'usuario_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    data = request.get_json()
    cartas_jugador = data.get('cartas_jugador')
    cartas_crupier = data.get('cartas_crupier')
    dinero_jugado = data.get('dinero_jugado')
    gano = data.get('gano') 
    print("Datos recibidos:", cartas_jugador, cartas_crupier, dinero_jugado, gano)
    usuario = db.session.get(Usuario, session['usuario_id'])

    if not all([cartas_jugador, cartas_crupier]) or dinero_jugado is None:
        return jsonify({'success': False, 'error': 'Datos incompletos'}), 400
    print("Datos recibidos:", cartas_jugador, cartas_crupier, dinero_jugado, gano)
    # Actualizar dinero
    if gano == "gano":
        dinero_ganado = dinero_jugado * 2
    elif gano == "perdio":
        dinero_ganado = 0  
    else:
        dinero_ganado = dinero_jugado
    
    usuario.dinero += (dinero_ganado - dinero_jugado)

    nuevo = ResultadosBlackjack(
        id_usuario=usuario.id,
        cartas_jugador=cartas_jugador,
        cartas_crupier=cartas_crupier,
        dinero_invertido=dinero_jugado,
        dinero_ganado=dinero_ganado
    )

    db.session.add(nuevo)
    db.session.commit()

    return jsonify({'success': True, 'saldo_actual': round(usuario.dinero, 2)})
    

#metodo para guardar los "depositos" de dinero
bp_deposito = Blueprint('depositar_dinero', __name__)

@bp_deposito.route('/depositar_dinero', methods=['GET', 'POST'])
def depositar_dinero():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            monto = float(request.form.get('monto', 0))
        except ValueError:
            return "Monto inválido", 400

        if monto <= 0:
            return "Monto debe ser mayor a 0", 400

        usuario = db.session.get(Usuario, session['usuario_id'])
        if not usuario:
            return "Usuario no encontrado", 404

        # Actualizar saldo del usuario
        usuario.dinero = (usuario.dinero or 0) + monto

        # Registrar en la tabla de depósitos
        nuevo_deposito = Deposito(
            id_usuario=usuario.id,
            cantidad=monto
        )
        db.session.add(nuevo_deposito)
        db.session.commit()

        flash("Depósito exitoso.")
        return redirect(url_for('principal'))  # Puedes redirigir a donde gustes

    return render_template("transactions/depositar.html")

#metodo para guardar el resultado del juego de snake
bp_snake_resultado = Blueprint('snake_resultado', __name__)

@bp_snake_resultado.route('/guardar_resultado_snake', methods=['POST'])
def guardar_resultado_snake():
    if 'usuario_id' not in session:
        return jsonify({"error": "No autenticado"}), 401

    data = request.get_json()
    puntos = data.get('puntuacion', 0)

    if puntos > 0:
        resultado = ResultadosSnake(
            id_usuario=session['usuario_id'],
            puntuacion=puntos
        )
        db.session.add(resultado)
        db.session.commit()

    return jsonify({"ok": True})

#metodo para guardar la cuenta bancaria
bp_cuenta = Blueprint('cuenta', __name__)

@bp_cuenta.route('/guardar_cuenta_bancaria', methods=['POST'])
def guardar_cuenta_bancaria():
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para guardar una cuenta bancaria.", "error")
        return redirect(url_for('login'))

    nombre_banco = request.form.get('nombre_banco', '').strip()
    cedula = request.form.get('cedula', '').strip()
    numero_cuenta = request.form.get('numero_cuenta', '').strip()

    # Validación: campos vacíos
    if not nombre_banco or not cedula or not numero_cuenta:
        flash("Todos los campos son obligatorios.", "error")
        return redirect(url_for('Cuenta_bancaria'))

    nueva_cuenta = CuentaBancaria(
        id_usuario=session['usuario_id'],
        nombre_banco=nombre_banco,
        cedula=cedula,
        numero_cuenta=numero_cuenta
    )

    db.session.add(nueva_cuenta)
    db.session.commit()

    flash("Cuenta bancaria guardada con éxito.", "success")
    return redirect(url_for('Cuenta_bancaria'))

#metodo para "retirar" dinero 
bp_retira = Blueprint('retirar_dinero', __name__)

@bp_retira.route('/retirar_dinero', methods=['GET', 'POST'])
def vista_retirar():
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para retirar.", "error")
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']
    cuentas = CuentaBancaria.query.filter_by(id_usuario=usuario_id).all()

    if request.method == 'POST':
        cuenta_id = request.form.get('cuenta_id')
        cantidad = request.form.get('cantidad')

        if not cuenta_id or not cantidad:
            flash("Por favor, completa todos los campos.", "error")
            return redirect(url_for('retirar'))

        try:
            cantidad = float(cantidad)
            usuario = Usuario.query.get(usuario_id)

            if usuario.dinero is None or usuario.dinero < cantidad:
                flash("Fondos insuficientes.", "error")
                return redirect(url_for('retirar'))

            retiro_nuevo = retirar(id_usuario=usuario_id, id_cuenta=cuenta_id, cantidad=cantidad)
            usuario.dinero -= cantidad

            db.session.add(retiro_nuevo)
            db.session.commit()
            flash("Retiro solicitado correctamente.", "success")
        except ValueError:
            flash("Cantidad inválida.", "error")

        return redirect(url_for('retirar'))

    # Cuando sea GET (llamado desde AJAX o algo similar)
    return jsonify([{
        'id': cuenta.id,
        'nombre_banco': cuenta.nombre_banco,
        'numero_cuenta': cuenta.numero_cuenta
    } for cuenta in cuentas])


estadisticas_bp = Blueprint('estadisticas', __name__)

def obtener_estadisticas(tipo, alcance):
    modelos = {
        'ruleta': ResultadosRuleta,
        'tragaperras': ResultadosTragaperras,
        'snake': ResultadosSnake
    }

    modelo = modelos.get(tipo)
    if not modelo:
        return None

    if tipo == 'ruleta':
        campo_resultado = modelo.resultado
        campo_usuario = modelo.id_usuario
    elif tipo == 'snake':
        campo_resultado = modelo.puntuacion
        campo_usuario = modelo.id_usuario
    elif tipo == 'tragaperras':
        campo_resultado = db.func.concat(modelo.resultado1, '-', modelo.resultado2, '-', modelo.resultado3)
        campo_usuario = modelo.id_usuario

    consulta = db.session.query(campo_resultado.label('resultado'), db.func.count(campo_usuario).label('cantidad'))

    if alcance == 'propias' and 'usuario_id' in session:
        consulta = consulta.filter(campo_usuario == session['usuario_id'])

    resultados = consulta.group_by('resultado').all()

    # Devolver diccionario resultado: cantidad
    return {resultado: cantidad for resultado, cantidad in resultados}

@estadisticas_bp.route('/estadisticas', methods=['GET', 'POST'])
def mostrar_estadisticas():
    if request.method == 'POST':
        tipo = request.form.get('tipo', 'ruleta')
        alcance = request.form.get('alcance', 'global')
        print(f"[POST] Tipo recibido: {tipo}, Alcance recibido: {alcance}")
        return redirect(url_for('estadisticas.mostrar_estadisticas', tipo=tipo, alcance=alcance))

    tipo = request.args.get('tipo', 'ruleta')
    alcance = request.args.get('alcance', 'global')
    print(f"[GET] Tipo recibido: {tipo}, Alcance recibido: {alcance}")

    data = obtener_estadisticas(tipo, alcance)
    if data is None:
        flash("Tipo de juego no válido", "error")
        return redirect(url_for('estadisticas.mostrar_estadisticas'))

    return render_template("estadisticas.html", data=data, tipo=tipo, alcance=alcance)

# Opcional: ruta para AJAX si la quieres usar
@estadisticas_bp.route('/obtener_datos', methods=['POST'])
def obtener_datos():
    tipo = request.form.get('tipo', 'ruleta')
    alcance = request.form.get('alcance', 'global')

    data = obtener_estadisticas(tipo, alcance) or {}
    print("Datos generados:", data)
    return {"data": data}