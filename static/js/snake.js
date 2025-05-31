let score = 0;
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const grid = 16;
const proximity = 1;
let count = 0;

const snake = { x: 160, y: 160, dx: grid, dy: 0, cells: [], maxCells: 4 };
const apple = { x: 320, y: 320 };

function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min)) + min;
}

function resetSnake() {
  snake.x = 160;
  snake.y = 160;
  snake.cells = [];
  snake.maxCells = 4;
  snake.dx = grid;
  snake.dy = 0;
  apple.x = getRandomInt(0, 25) * grid;
  apple.y = getRandomInt(0, 25) * grid;
}

function updateScore() {
  const scoreDisplay = document.getElementById('score');
  scoreDisplay.innerText = 'Puntuación: ' + score;
  scoreDisplay.classList.add('flash');
  setTimeout(() => scoreDisplay.classList.remove('flash'), 400);
}

function reiniciarJuego() {
  score = 0;
  updateScore();
  resetSnake();
}

function loop() {
  requestAnimationFrame(loop);
  if (++count < 4) return;
  count = 0;

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  snake.x += snake.dx;
  snake.y += snake.dy;

  if (snake.x < 0) snake.x = canvas.width - grid;
  else if (snake.x >= canvas.width) snake.x = 0;
  if (snake.y < 0) snake.y = canvas.height - grid;
  else if (snake.y >= canvas.height) snake.y = 0;

  snake.cells.unshift({ x: snake.x, y: snake.y });
  if (snake.cells.length > snake.maxCells) snake.cells.pop();

  ctx.fillStyle = 'red';
  ctx.fillRect(apple.x, apple.y, grid - 1, grid - 1);

  ctx.fillStyle = 'lime';
  snake.cells.forEach((cell, index) => {
    ctx.fillRect(cell.x, cell.y, grid - 1, grid - 1);
    const distance = Math.abs(cell.x - apple.x) + Math.abs(cell.y - apple.y);
    if (distance <= proximity * grid) {
      snake.maxCells++;
      apple.x = getRandomInt(0, 25) * grid;
      apple.y = getRandomInt(0, 25) * grid;
      score++;
      updateScore();
    }

    for (let i = index + 1; i < snake.cells.length; i++) {
      if (cell.x === snake.cells[i].x && cell.y === snake.cells[i].y) {
        fetch('/guardar_resultado_snake', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ puntuacion: score })
        });

        alert('¡Has perdido! Tu puntuación es: ' + score);
        score = 0;
        updateScore();
        resetSnake();
        break;
      }
    }
  });
}

document.addEventListener('keydown', (e) => {
  if (e.which === 37 && snake.dx === 0) { snake.dx = -grid; snake.dy = 0; }
  else if (e.which === 38 && snake.dy === 0) { snake.dy = -grid; snake.dx = 0; }
  else if (e.which === 39 && snake.dx === 0) { snake.dx = grid; snake.dy = 0; }
  else if (e.which === 40 && snake.dy === 0) { snake.dy = grid; snake.dx = 0; }
});

resetSnake();
updateScore();
requestAnimationFrame(loop);