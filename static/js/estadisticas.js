document.addEventListener('DOMContentLoaded', function () {
  if (typeof data !== 'undefined' && Object.keys(data).length > 0) {
    const ctx = document.getElementById('grafico').getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: Object.keys(data),
        datasets: [{
          label: 'Cantidad',
          data: Object.values(data),
          backgroundColor: 'rgba(0, 255, 255, 0.5)',
          borderColor: 'aqua',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              color: 'white'
            }
          },
          x: {
            ticks: {
              color: 'white'
            }
          }
        },
        plugins: {
          legend: {
            labels: {
              color: 'white'
            }
          }
        }
      }
    });
  } else {
    document.getElementById('grafico').style.display = 'none';
  }
});