const symbols = ['🍒', '🍋', '🍉', '🍇', '⭐', '🔔'];
let jugadas = 0;
let ganadas = 0;
let spinning = false;

function fillReelWithSymbols(reelId, reelSymbols) {
  const container = document.getElementById(reelId);
  container.innerHTML = '';
  for (let i = 0; i < 20; i++) {
    const div = document.createElement('div');
    div.className = 'symbol';
    div.textContent = reelSymbols[i % reelSymbols.length];
    container.appendChild(div);
  }
}

function spin() {
  if (spinning) return;
  spinning = true;

  const reels = ['symbols1', 'symbols2', 'symbols3'];
  const results = [];
  const stopIndices = [];
  const resultEl = document.getElementById('result');
  resultEl.textContent = '';
  resultEl.classList.remove('result-win');

  jugadas++;
  document.getElementById('jugadas').textContent = jugadas;

  reels.forEach((id, i) => {
    const stopIndex = Math.floor(Math.random() * 17) + 2;
    stopIndices[i] = stopIndex;

    const finalSymbol = symbols[Math.floor(Math.random() * symbols.length)];
    results[i] = finalSymbol;

    let reelSymbols = [];
    for (let j = 0; j < 20; j++) {
      reelSymbols.push(j === stopIndex ? finalSymbol : symbols[Math.floor(Math.random() * symbols.length)]);
    }

    fillReelWithSymbols(id, reelSymbols);
  });

  reels.forEach((id, i) => {
    const el = document.getElementById(id);
    const offset = -100 * stopIndices[i];
    el.style.transition = 'transform 2s cubic-bezier(0.33, 1, 0.68, 1)';
    setTimeout(() => {
      el.style.transform = `translateY(${offset}px)`;
    }, i * 300);
  });

  const totalDelay = 2300 + (reels.length - 1) * 300;
  setTimeout(() => {
    const [a, b, c] = results;
    if (a === b && b === c) {
      ganadas++;
      resultEl.textContent = "🎉 ¡Ganaste! 🎉";
      resultEl.classList.add('result-win');
    } else {
      resultEl.textContent = "Intenta de nuevo...";
    }
    document.getElementById('ganadas').textContent = ganadas;

    fetch('/guardar_resultado_tragamonedas', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        resultado1: a,
        resultado2: b,
        resultado3: c,
        ganado: a === b && b === c,
        dinero_jugado: 10
      })
    })
      .then(res => res.json())
      .then(data => {
        if (data.saldo_actual !== undefined) {
          document.getElementById('saldo').textContent = `Saldo: $${data.saldo_actual.toFixed(2)}`;
        } else if (data.error) {
          alert('Error: ' + data.error);
        }
      })
      .catch(err => {
        console.error('Error al guardar resultado:', err);
      })
      .finally(() => {
        spinning = false;
      });
  }, totalDelay);
}