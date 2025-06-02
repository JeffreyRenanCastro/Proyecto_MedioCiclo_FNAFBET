const miModulo = (() => {
    'use strict'

    // Arreglos y constantes para el manejo del deck
    let deck = [];
    const tipos = ['C', 'D', 'H', 'S'],
        especiales = ['A', 'J', 'K', 'Q'];

    // Referencias HTML
    const btnPedir = document.querySelector('#btnPedir'),
        btnDetener = document.querySelector('#btnDetener'),
        btnNuevo = document.querySelector('#btnNuevo');

    const puntosHTML = document.querySelectorAll('.content-player span'),
        divCartasJugadores = document.querySelectorAll('.divCartas');

    let puntosJugadores = [];

    // FUNCIONES
    const inicializarJuego = (numJugadores = 2) => {
        const apuestaInput = document.getElementById('apuesta');
        const apuesta = parseFloat(apuestaInput.value);

        if (isNaN(apuesta) || apuesta <= 0) {
            alert("Por favor, ingrese una apuesta válida.");
            return;
        }

        apuestaInput.disabled = true;

        document.getElementById('resultado').innerHTML = '';
        document.querySelector('.resultado-box').style.background = 'none';

        deck = crearDeck();
        puntosJugadores = [];

        for (let i = 0; i < numJugadores; i++) {
            puntosJugadores.push(0);
        }

        puntosHTML.forEach(elem => elem.innerText = 0);
        divCartasJugadores.forEach(elem => elem.innerHTML = '');

        btnDetener.disabled = false;
        btnPedir.disabled = false;
    }

    // Crear y barajar el deck
    const crearDeck = () => {
        deck = [];

        for (let i = 2; i <= 10; i++) {
            for (let tipo of tipos) {
                deck.push(i + tipo);
            }
        }

        for (let especial of especiales) {
            for (let tipo of tipos) {
                deck.push(especial + tipo);
            }
        }

        return _.shuffle(deck); // underscore.js
    }

    const pedirCarta = () => {
        if (deck.length === 0) throw 'No hay cartas en el deck';
        return deck.pop();
    }

    const valorCarta = (carta) => {
        const valor = carta.substring(0, carta.length - 1);
        return isNaN(valor) ? (valor === 'A' ? 11 : 10) : valor * 1;
    }

    const acumularPuntos = (carta, turno) => {
        puntosJugadores[turno] += valorCarta(carta);
        puntosHTML[turno].innerText = puntosJugadores[turno];
        return puntosJugadores[turno];
    }

    const crearCarta = (carta, turno) => {
        const imgCarta = document.createElement('img');
        imgCarta.src = `static/image/cartas/${carta}.png`;
        imgCarta.classList.add('carta');
        divCartasJugadores[turno].append(imgCarta);
    }

    const determinarGanador = () => {
        const [puntosMinimos, puntosComputadora] = puntosJugadores;
        const resultadoBox = document.querySelector('.resultado-box');
        const mensajeResultado = document.getElementById('resultado');

        resultadoBox.style.background = '#333333';
        let mensaje = `
        <p>Jugador: <b>${puntosMinimos}</b> - Computadora: <b>${puntosComputadora}</b></p>
    `;

        let gano = "perdio";
        if (puntosMinimos === puntosComputadora) {
            mensaje += `<p><b>¡Empate!</b></p>`;
            gano = "empate";
        } else if ((puntosMinimos > puntosComputadora && puntosMinimos <= 21) || puntosComputadora > 21) {
            mensaje += `<p class="text-success"><b>¡Ganaste!</b></p>`;
            gano = "gano";
        } else {
            mensaje += `<p class="text-danger"><b>¡Perdiste!</b></p>`;
        }

        mensaje += `<div id='saldo'></div>`;

        mensajeResultado.innerHTML = mensaje;

        mensajeResultado.innerHTML = mensaje;

        guardarResultado(gano);

    };

    const guardarResultado = (gano) => {
        const cartasJugador = Array.from(divCartasJugadores[0].querySelectorAll('img')).map(img => img.src.split('/').pop().replace('.png', ''));
        const cartasCrupier = Array.from(divCartasJugadores[1].querySelectorAll('img')).map(img => img.src.split('/').pop().replace('.png', ''));

        fetch('/guardar_resultado_blackjack', {
            
            method: 'POST',
            headers: {'Content-Type': 'application/json' },
            body: JSON.stringify({
                cartas_jugador: cartasJugador.join(','),
                cartas_crupier: cartasCrupier.join(','),
                dinero_jugado: parseFloat(document.getElementById('apuesta').value),
                gano: gano
            })
        })
            .then(res => res.json())
            .then(data => {
                if (data.saldo_actual !== undefined) {
                    document.getElementById('saldo').innerText = `Saldo: $${data.saldo_actual}`;
                } else {
                    console.error(data);
                }
            })
            .catch(err => console.error("Error al guardar resultado:", err))
            .finally(() => {
                document.getElementById('apuesta').disabled = false;
            });
    };

    const turnoComputadora = (puntosMinimos) => {
        let puntosComputadora = 0;

        do {
            const carta = pedirCarta();
            puntosComputadora = acumularPuntos(carta, puntosJugadores.length - 1);
            crearCarta(carta, puntosJugadores.length - 1);
        } while (puntosComputadora < puntosMinimos && puntosMinimos <= 21);

        determinarGanador();
    }

    // EVENTOS
    btnPedir.addEventListener('click', () => {
        const carta = pedirCarta();
        const puntosJugador = acumularPuntos(carta, 0);
        crearCarta(carta, 0);

        if (puntosJugador > 21) {
            btnPedir.disabled = true;
            btnDetener.disabled = true;
            turnoComputadora(puntosJugador);
        } else if (puntosJugador === 21) {
            btnPedir.disabled = true;
            btnDetener.disabled = true;
            turnoComputadora(puntosJugador);
        }
    });

    btnDetener.addEventListener('click', () => {
        btnDetener.disabled = true;
        btnPedir.disabled = true;
        turnoComputadora(puntosJugadores[0]);
    });

    btnNuevo.addEventListener('click', () => {
        inicializarJuego();
    });

    return {
        nuevoJuego: inicializarJuego
    };

})();

