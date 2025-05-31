let jugadorActual = '⭕';
let juegoActivo = true;
let tablero = ['', '', '', '', '', '', '', '', ''];
const info = document.getElementById('juego-info');
const cuadros = document.querySelectorAll('.cuadro');
const btnReiniciar = document.querySelector('.juego-boton button');

const combinacionesGanadoras = [
  [0, 1, 2], [3, 4, 5], [6, 7, 8], // filas
  [0, 3, 6], [1, 4, 7], [2, 5, 8], // columnas
  [0, 4, 8], [2, 4, 6]           // diagonales
];

function actualizarInfo(mensaje) {
  info.textContent = mensaje;
}

function verificarGanador() {
  for (let combinacion of combinacionesGanadoras) {
    const [a, b, c] = combinacion;
    if (tablero[a] && tablero[a] === tablero[b] && tablero[a] === tablero[c]) {
      juegoActivo = false;
      actualizarInfo(`🎉 ¡${tablero[a]} gana!`);
      return;
    }
  }

  if (!tablero.includes('')) {
    juegoActivo = false;
    actualizarInfo("🤝 ¡Empate!");
  }
}

function manejarClick(index) {
  if (!juegoActivo || tablero[index]) return;

  tablero[index] = jugadorActual;
  cuadros[index].textContent = jugadorActual;

  cuadros[index].classList.add(jugadorActual === '⭕' ? 'o-azul' : 'x-rojo');

  verificarGanador();

  if (juegoActivo) {
    jugadorActual = jugadorActual === '⭕' ? '❌' : '⭕';
    actualizarInfo(`Turno de ${jugadorActual}`);
  }
}

function reiniciarJuego() {
  jugadorActual = '⭕';
  juegoActivo = true;
  tablero = ['', '', '', '', '', '', '', '', ''];
  cuadros.forEach(c => {
    c.textContent = '';
    c.classList.remove('o-azul', 'x-rojo');
  });
  actualizarInfo(`Turno de ${jugadorActual}`);
}

// Asignar eventos a los cuadros
cuadros.forEach((cuadro, index) => {
  cuadro.addEventListener('click', () => manejarClick(index));
});

// Botón de reinicio
btnReiniciar.addEventListener('click', reiniciarJuego);

// Inicializar mensaje
actualizarInfo(`Turno de ${jugadorActual}`);
