function closeAlert(button) {
  const alert = button.closest('.alert');
  if (alert) {
    alert.classList.add('hide');
    setTimeout(() => alert.remove(), 500);
  }
}

// Cierre automático a los 5 segundos
setTimeout(() => {
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    alert.classList.add('hide');
    setTimeout(() => alert.remove(), 500);
  });
}, 5000);

// Actualizar dinamicamente el dinero disponible del usuario
  const dropdown = document.querySelector('.dropdown');
  const dineroSpan = document.getElementById('dinero-usuario');

  dropdown.addEventListener('show.bs.dropdown', () => {
    fetch('/auth/dinero_usuario')
      .then(response => response.json())
      .then(data => {
        if (data.dinero !== undefined) {
          dineroSpan.textContent = data.dinero.toFixed(2);
        }
      })
      .catch(error => {
        console.error('Error al obtener el dinero del usuario:', error);
      });
  });