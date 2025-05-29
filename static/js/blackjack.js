// === SONIDOS ===
const boton1 = document.querySelector("#button1");
const boton2 = document.querySelector("#button2");
const boton3 = document.querySelector("#button3");
const mensajeDerecha = document.querySelector("#textright");
const mensajeIzquierda = document.querySelector("#textleft");
const saldo = document.querySelector("#balance");
const cartaCrupier = document.querySelector("#dealercard");
const cartaJugador = document.querySelector("#yourcard");

let sonidoCarta = new Audio('Sounds/drawcard.mp3');
let sonidoGanaCrupier = new Audio('Sounds/dealerwin.wav');
let sonidoGanaJugador = new Audio('Sounds/playerwin.mp3');
let sonidoEmpate = new Audio('Sounds/gamedrawsound.wav');

sonidoCarta.volume = 0.1;
sonidoGanaCrupier.volume = 0.1;
sonidoGanaJugador.volume = 0.1;
sonidoEmpate.volume = 0.1;

let dinero = parseInt(saldo.innerText);
let juegoActivo = false;

const mazo = [
    ...["Corazones", "Diamantes", "Tréboles", "Picas"].flatMap(palo => [
        { tipo: 'A', valor: 11 },
        ...Array.from({ length: 9 }, (_, i) => ({ tipo: (i + 2).toString(), valor: i + 2 })),
        { tipo: '10', valor: 10 },
        { tipo: 'J', valor: 10 },
        { tipo: 'Q', valor: 10 },
        { tipo: 'K', valor: 10 },
    ].map(carta => ({ ...carta, palo })))
];

let contadorJugador = 0;
let sumaJugador = 0;
let sumaCrupier = 0;
let ganador;
let apuesta;

function sacarCarta() {
    sonidoCarta.play();
    const indice = Math.floor(Math.random() * mazo.length);
    const carta = mazo[indice];
    if (carta.tipo === 'A' && contadorJugador <= 1) return { ...carta, valor: 11 };
    else if (carta.tipo === 'A') return { ...carta, valor: 1 };
    return carta;
}

function sacarJugador() {
    const carta = sacarCarta();
    contadorJugador++;
    document.querySelector("#suitU").innerText = carta.palo;
    document.querySelector("#typeU").innerText = carta.tipo;
    sumaJugador += carta.valor;
    document.querySelector("#valueU").innerText = sumaJugador;

    mensajeIzquierda.style.color = "aliceblue";
    if (sumaJugador < 21) sacarCrupier();
    else verificarGanador();
}

function sacarCrupier() {
    if (sumaCrupier < 17 || sumaCrupier < sumaJugador) {
        const carta = sacarCarta();
        document.querySelector("#suitD").innerText = carta.palo;
        document.querySelector("#typeD").innerText = carta.tipo;
        sumaCrupier += carta.valor;
        document.querySelector("#valueD").innerText = sumaCrupier;

        if (sumaCrupier === 21) {
            mostrarResultado("Crupier gana", sonidoGanaCrupier, "red");
        } else if (sumaCrupier > 21) {
            dinero += 2 * apuesta;
            mostrarResultado("Ganaste", sonidoGanaJugador, "rgb(3,255,3)");
        }
    } else {
        verificarGanador();
    }
}

function verificarGanador() {
    juegoActivo = false;
    actualizarUbicacion(ubicaciones[0]);

    if (sumaCrupier > 21) ganador = 'Jugador';
    else if (sumaJugador > 21) ganador = 'Crupier';
    else if (sumaJugador === 21) ganador = 'Jugador';
    else if (sumaCrupier === 21) ganador = 'Crupier';
    else if (sumaJugador === sumaCrupier) ganador = 'Empate';
    else ganador = sumaJugador > sumaCrupier ? 'Jugador' : 'Crupier';

    if (ganador === 'Jugador') {
        dinero += 2 * apuesta;
        mostrarResultado("Ganaste", sonidoGanaJugador, "rgb(3,255,3)");
    } else if (ganador === 'Crupier') {
        mostrarResultado("Crupier gana", sonidoGanaCrupier, "red");
    } else {
        dinero += apuesta;
        mostrarResultado("Empate", sonidoEmpate, "#ffbd08");
    }

    saldo.innerText = dinero;
    contadorJugador = 0;
    sumaJugador = 0;
    sumaCrupier = 0;
}

function mostrarResultado(texto, sonido, color) {
    mensajeIzquierda.innerText = texto;
    mensajeIzquierda.style.color = color;
    sonido.play();
}

function apostar(cantidad) {
    if (dinero >= cantidad && !juegoActivo) {
        dinero -= cantidad;
        saldo.innerText = dinero;
        actualizarUbicacion(ubicaciones[1]);
        juegoActivo = true;
        mostrarCartas();
        sacarJugador();
        apuesta = cantidad;
    } else {
        alert(juegoActivo ? "Ya estás jugando" : "No tienes suficiente dinero");
    }
}

function plantarse() {
    if (juegoActivo && contadorJugador >= 2) {
        sacarCrupier();
        verificarGanador();
    } else {
        alert("Debes sacar al menos dos cartas antes de plantarte.");
    }
}

function doblar() {
    dinero -= apuesta;
    apuesta *= 2;
    saldo.innerText = dinero;
    mensajeDerecha.innerText = "Apuesta Doblada";
    sacarJugador();
}

function mostrarCartas() {
    if (juegoActivo) {
        setTimeout(() => {
            cartaJugador.style.display = "block";
            mensajeIzquierda.style.animationName = ''; 
            mensajeIzquierda.style.borderRight = 'none'; 
            setTimeout(() => cartaCrupier.style.display = "block", 1000);
        }, 1000);
    } else {
        cartaCrupier.style.display = "none";
        cartaJugador.style.display = "none";
    }
}

const ubicaciones = [
    {
        nombre: "Menú de Apuesta",
        "boton texto": ["$100", "$500", "$1000"],
        "boton funciones": [() => apostar(100), () => apostar(500), () => apostar(1000)],
        mensajeIzquierda: "Elige tu apuesta",
        mensajeDerecha: "Nueva apuesta",
    },
    {
        nombre: "Juego",
        "boton texto": ["Sacar", "Plantarse", "Doblar"],
        "boton funciones": [sacarJugador, plantarse, doblar],
        mensajeIzquierda: "Repartiendo...",
        mensajeDerecha: "Elige acción",
    }
];

function actualizarUbicacion(ubicacion) {
    boton1.innerText = ubicacion["boton texto"][0];
    boton2.innerText = ubicacion["boton texto"][1];
    boton3.innerText = ubicacion["boton texto"][2];
    boton1.onclick = ubicacion["boton funciones"][0];
    boton2.onclick = ubicacion["boton funciones"][1];
    boton3.onclick = ubicacion["boton funciones"][2];
    mensajeDerecha.innerText = ubicacion.mensajeDerecha;
    mensajeIzquierda.innerText = ubicacion.mensajeIzquierda;
}

actualizarUbicacion(ubicaciones[0]);
mostrarCartas();
mensajeIzquierda.innerText = 'Bienvenido al Blackjack';
mensajeDerecha.innerText = 'Elige tu apuesta';
