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
