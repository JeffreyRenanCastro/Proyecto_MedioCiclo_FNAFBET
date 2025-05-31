const canvas = document.getElementById('ruleta');
const ctx = canvas.getContext('2d');
const resultado = document.getElementById('resultado');

function actualizarOpciones() {
  const tipo = document.getElementById("tipo_apuesta").value;
  const select = document.getElementById("valor_apuesta");

  select.innerHTML = ""; // limpiar opciones previas

  if (tipo === "color") {
    ["rojo", "negro", "verde"].forEach(color => {
      const option = document.createElement("option");
      option.value = color;
      option.textContent = color.charAt(0).toUpperCase() + color.slice(1);
      select.appendChild(option);
    });
  } else {
    const numeros = [
      "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
      "11", "12", "13", "14", "15", "16", "17", "18", "19",
      "20", "21", "22", "23", "24", "25", "26", "27", "28",
      "29", "30", "31", "32", "33", "34", "35", "36", "00"
    ];
    numeros.forEach(num => {
      const option = document.createElement("option");
      option.value = num;
      option.textContent = num;
      select.appendChild(option);
    });
  }
}

// Ejecutar al cargar
document.addEventListener("DOMContentLoaded", actualizarOpciones);

const numeros = [
  "0", "28", "9", "26", "30", "11", "7", "20", "32", "17",
  "5", "22", "34", "15", "3", "24", "36", "13", "1", "00",
  "27", "10", "25", "29", "12", "8", "19", "31", "18", "6",
  "21", "33", "16", "4", "23", "35", "14", "2"
];

const colores = numeros.map(n => {
  if (n === "0" || n === "00")
    return "green";

  return ["23", "14", "9", "30", "7", "32", "5", "34", "3", "36", "1", "27", "25", "12", "19", "18", "21", "16"].includes(n) ? "red" : "black";
});

let angulo = 0;
const segmento = 2 * Math.PI / numeros.length;

function dibujarRuleta(rotacion = 0) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.save();
  ctx.translate(canvas.width / 2, canvas.height / 2);
  ctx.rotate(rotacion);
  for (let i = 0; i < numeros.length; i++) {
    ctx.beginPath();
    ctx.fillStyle = colores[i];
    ctx.moveTo(0, 0);
    ctx.arc(0, 0, 290, i * segmento, (i + 1) * segmento);
    ctx.lineTo(0, 0);
    ctx.fill();

    ctx.save();
    ctx.fillStyle = "white";
    ctx.rotate((i + 0.5) * segmento);
    ctx.translate(200, 0);
    ctx.rotate(Math.PI / 2);
    ctx.font = "20px Arial";
    ctx.fillText(numeros[i], -10, 0);
    ctx.restore();
  }
  ctx.restore();
}

async function girarRuleta() {
  const tipo = document.getElementById('tipo_apuesta').value;
  const valor = document.getElementById('valor_apuesta').value.toLowerCase();
  const cantidad = parseFloat(document.getElementById('dinero_apostado').value);

  if (!valor || isNaN(cantidad) || cantidad <= 0) {
    alert("Por favor ingresa valores válidos.");
    return;
  }

  try {
    const response = await fetch('/jugar_ruleta', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tipo_apuesta: tipo,
        valor_apuesta: valor,
        dinero_apostado: cantidad
      })
    });

    const data = await response.json();

    if (data.error) {
      resultado.textContent = `Error: ${data.error}`;
      return;
    }

    // Animación
    const indice = numeros.indexOf(data.resultado_numero.toString());
    const destino = 2 * Math.PI * (numeros.length - indice) / numeros.length;
    const vueltas = Math.floor(Math.random() * 3) + 5;
    const total = 2 * Math.PI * vueltas + destino;
    let start = null;

    function animar(timestamp) {
      if (!start) start = timestamp;
      const progreso = timestamp - start;
      const duracion = 4000;
      const easeOut = 1 - Math.pow(1 - progreso / duracion, 3);
      angulo = total * easeOut;
      dibujarRuleta(angulo);
      if (progreso < duracion) {
        requestAnimationFrame(animar);
      } else {
        resultado.innerHTML = `
              <p>Resultado: <b>${data.resultado_numero} (${data.resultado_color})</b></p>
              <p>${data.gano ? '¡Ganaste!' : 'Perdiste'} ${data.gano ? data.dinero_ganado + ' monedas' : ''}</p>
              <p>Saldo actual: ${data.saldo_actual} monedas</p>
            `;
      }
    }

    requestAnimationFrame(animar);

  } catch (error) {
    resultado.textContent = `Error en la conexión con el servidor`;
  }
}

dibujarRuleta();